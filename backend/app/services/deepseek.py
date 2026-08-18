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
            return {
                "score": score,
                "tier": tier,
                "rationale": result.get("rationale", ""),
                "model_used": self.model_id,
            }
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            score = _heuristic_score(signals)
            return {
                "score": score,
                "tier": tier_for_score(score),
                "rationale": "Model output could not be parsed; used heuristic scoring.",
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
    ) -> dict:
        highlights = "\n".join(f"- {s.get('title')}" for s in signal_highlights[:3]) or "- (personalize around the company)"
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
            + (f"USE THIS TEMPLATE AS A BASE (still personalize):\n{template.get('body', '')}\n" if template else "")
        )
        messages = [{"role": "user", "content": user_content}]
        text = await self._chat(system, messages, max_tokens=600, temperature=0.7)
        try:
            result = self._extract_json(text)
            return {"subject": result.get("subject", ""), "body": result.get("body", ""), "model_used": self.model_id}
        except (ValueError, KeyError, json.JSONDecodeError):
            subject = template.get("subject") if template else f"Quick question about {account.get('company_name')}"
            body = template.get("body") if template else f"Hi there, I noticed {account.get('company_name')} is active. Would you be open to a quick chat?"
            return {"subject": subject, "body": body, "model_used": "template"}