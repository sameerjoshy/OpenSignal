"""DeepSeek API client (OpenAI-compatible) - account scoring + personalized email generation."""

import json
import re

import httpx

from app.services.base import ServiceError, ServiceNotConfigured
from config import settings

DEFAULT_BASE_URL = "https://api.deepseek.com"


def tier_for_score(score: float) -> int:
    if score >= 70:
        return 1
    if score >= 40:
        return 2
    return 3


def _heuristic_score(signals: list[dict]) -> float:
    weights = {
        "funding": 25,
        "acquisition": 22,
        "website_intent": 20,
        "job_change": 18,
        "key_decision_maker": 12,
        "major_event": 15,
        "leadership": 14,
        "product_launch": 12,
        "earnings": 8,
        "news": 5,
        "manual": 10,
    }
    score = min(100, sum(weights.get(s.get("signal_type", "news"), 5) for s in signals) + 10)
    return round(score, 1)


class DeepSeekClient:
    """Minimal DeepSeek chat-completions client (OpenAI-compatible API)."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or settings.deepseek_api_key
        if not key:
            raise ServiceNotConfigured("deepseek")
        self.api_key = key
        self.base_url = (settings.deepseek_base_url or DEFAULT_BASE_URL).rstrip("/")
        self.model_id = settings.deepseek_model_id

    async def _chat(
        self,
        system: str,
        messages: list[dict],
        max_tokens: int = 1500,
        temperature: float = 0.3,
    ) -> str:
        payload = {
            "model": self.model_id,
            "messages": [{"role": "system", "content": system}, *messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise ServiceError(f"DeepSeek request failed: {exc}", status_code=502) from exc
        if resp.status_code >= 400:
            raise ServiceError(
                f"DeepSeek API error ({resp.status_code}): {resp.text[:300]}", status_code=502
            )
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ServiceError("DeepSeek returned an unexpected response") from exc

    @staticmethod
    def _extract_json(text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ServiceError("DeepSeek returned invalid JSON")
        return json.loads(match.group(0))

    @staticmethod
    def sanitize_email_fields(subject: str, body: str) -> tuple[str, str]:
        """Strip header-injection / control characters from AI-generated fields."""
        clean_subject = re.sub(r"[\r\n\x00-\x1f\x7f]+", " ", subject).strip()
        clean_body = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+", "", body).strip()
        return clean_subject, clean_body

    async def score_account(self, account: dict, signals: list[dict]) -> dict:
        signal_lines = "\n".join(
            f"- [{s.get('source')} / {s.get('signal_type')}] {s.get('title')}" for s in signals
        ) or "- (no signals detected yet)"
        system = (
            "You are an expert B2B demand generation analyst. Score how likely the given company is "
            "currently buying or evaluating new solutions, based on the buying signals observed.\n"
            "Return ONLY JSON with this exact shape:\n"
            '{"score": <int 0-100>, "tier": <1|2|3>, "rationale": "<2-3 sentence explanation>"}\n'
            "Tier rules: score >= 70 => 1 (hot, multi-channel now), 40-69 => 2 (warm, email sequence), "
            "score < 40 => 3 (nurture, low priority)."
        )
        messages = [
            {
                "role": "user",
                "content": (
                    f"COMPANY:\n- Name: {account.get('company_name')}\n- Domain: {account.get('domain') or 'unknown'}\n"
                    f"- Industry: {account.get('industry') or 'unknown'}\n- Size: {account.get('employee_count') or 'unknown'} employees\n\n"
                    f"SIGNALS:\n{signal_lines}\n\n"
                    "Provide the JSON score now."
                ),
            }
        ]
        text = await self._chat(system, messages, max_tokens=500, temperature=0.2)
        try:
            result = self._extract_json(text)
            score = float(result.get("score", 0))
            tier = int(result.get("tier", tier_for_score(score)))
            # Enforce the documented mapping so a model glitch can't misroute hot accounts.
            enforced_tier = tier_for_score(score)
            return {
                "score": score,
                "tier": enforced_tier,
                "rationale": result.get("rationale", ""),
                "model_used": self.model_id,
            }
        except ServiceError:
            return self._heuristic_fallback(signals, "Model request failed; used heuristic scoring.")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return self._heuristic_fallback(signals, "Model output could not be parsed; used heuristic scoring.")

    @staticmethod
    def _heuristic_fallback(signals: list[dict], rationale: str) -> dict:
        score = _heuristic_score(signals)
        return {
            "score": score,
            "tier": tier_for_score(score),
            "rationale": rationale,
            "model_used": "heuristic",
        }

    async def generate_email(
        self,
        *,
        account: dict,
        campaign: dict,
        signal_highlights: list[dict],
        sender_name: str,
        sender_title: str,
        product_context: str,
        sequence_step: int,
        template: dict | None = None,
        variant: str = "A",
    ) -> dict:
        highlights = "\n".join(f"- {s.get('title')}" for s in signal_highlights[:3]) or "- (personalize around the company)"
        variant_rule = ""
        if variant == "B":
            variant_rule = (
                "VARIANT: This is variant B of an A/B test. Write a DIFFERENT angle and subject line "
                "from variant A - try a curiosity-style subject or a different CTA, keep the same core value proposition.\n"
            )
        system = (
            "You are a senior demand generation copywriter writing a short, human, high-open-rate "
            "outbound email. It must be personalized to the specific account and reference real signals. "
            "No fluff, no buzzwords, max 120 words for the body.\n"
            "Return ONLY JSON: {\"subject\": \"...\", \"body\": \"...\"}"
        )
        user_content = (
            f"SENDER: {sender_name}, {sender_title}\n"
            f"PRODUCT/SERVICE: {product_context}\n\n"
            f"TARGET COMPANY: {account.get('company_name')} ({account.get('industry') or 'unknown industry'})\n"
            f"RECENT SIGNALS:\n{highlights}\n\n"
            f"SEQUENCE STEP: {sequence_step}\n"
            f"{variant_rule}"
            + (f"USE THIS TEMPLATE AS A BASE (still personalize):\n{template.get('body', '')}\n" if template else "")
        )
        messages = [{"role": "user", "content": user_content}]
        text = await self._chat(system, messages, max_tokens=600, temperature=0.7 if variant == "B" else 0.5)
        try:
            result = self._extract_json(text)
            subject, body = self.sanitize_email_fields(
                result.get("subject", ""), result.get("body", "")
            )
            return {"subject": subject, "body": body, "model_used": self.model_id}
        except ServiceError:
            return self._template_fallback(
                account, template, "Model request failed; used template."
            )
        except (ValueError, KeyError, json.JSONDecodeError):
            return self._template_fallback(
                account, template, "Model output could not be parsed; used template."
            )

    @staticmethod
    def _template_fallback(account: dict, template: dict | None, note: str) -> dict:
        subject = template.get("subject") if template else f"Quick question about {account.get('company_name')}"
        body = template.get("body") if template else f"Hi there, I noticed {account.get('company_name')} is active. Would you be open to a quick chat?"
        return {"subject": subject, "body": body, "model_used": "template", "note": note}

    async def classify_reply(self, subject: str, body: str) -> dict:
        """Classify an inbound reply: hot | not_interested | question | out_of_office."""
        system = (
            "You classify B2B outbound email replies. Return ONLY JSON with this exact shape:\n"
            '{"classification": "hot|not_interested|question|out_of_office", "confidence": <0.0-1.0>, '
            '"summary": "<one short sentence>", "interested": <true|false>}'
        )
        user_content = f"SUBJECT: {subject}\n\nREPLY BODY:\n{body[:4000]}"
        messages = [{"role": "user", "content": user_content}]
        text = await self._chat(system, messages, max_tokens=300, temperature=0.1)
        try:
            result = self._extract_json(text)
            classification = result.get("classification", "review")
            if classification not in ("hot", "not_interested", "question", "out_of_office"):
                classification = "review"
            return {
                "classification": classification,
                "confidence": float(result.get("confidence", 0.6)),
                "summary": result.get("summary", ""),
                "interested": bool(result.get("interested", False)),
            }
        except ServiceError:
            return self._rule_reply_classification(subject, body)
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._rule_reply_classification(subject, body)

    @staticmethod
    def _rule_reply_classification(subject: str, body: str) -> dict:
        """Offline, deterministic reply classifier used when the model is unavailable."""
        text = f"{subject}\n{body}".lower()
        if any(k in text for k in ("out of office", "ooo ", "on vacation", "vacation", "will return")):
            return {"classification": "out_of_office", "confidence": 0.8, "summary": "Auto-reply / out of office.", "interested": False}
        if any(k in text for k in ("unsubscribe", "not interested", "stop emailing", "remove me", "no longer interested", "take me off")):
            return {"classification": "not_interested", "confidence": 0.8, "summary": "Explicitly not interested.", "interested": False}
        if "?" in body or any(k in text for k in ("what is", "how much", "pricing", "how does", "more details", "tell me about")):
            return {"classification": "question", "confidence": 0.6, "summary": "Prospect asked a question.", "interested": True}
        return {"classification": "review", "confidence": 0.4, "summary": "", "interested": False}

    async def suggest_reply(self, original_body: str, reply_body: str) -> str:
        """Draft a human-sounding reply to a question from a prospect."""
        system = (
            "You are a senior sales rep replying to a prospect's question about a B2B service. "
            "Write a warm, concise, helpful reply that answers the question directly and moves to a "
            "call/meeting. Max 150 words. Return ONLY the reply text, no preamble."
        )
        messages = [
            {
                "role": "user",
                "content": (
                    f"OUR ORIGINAL EMAIL:\n{original_body[:3000]}\n\n"
                    f"PROSPECT REPLY:\n{reply_body[:3000]}\n\n"
                    "Write the reply now."
                ),
            }
        ]
        return (await self._chat(system, messages, max_tokens=400, temperature=0.5)).strip()