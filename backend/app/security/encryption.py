"""AES-256-GCM encryption for API credentials (acceptance: credentials encrypted at rest)."""

import base64
import json
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import settings

_CONFIG_MARKER = "$enc"


def _key() -> bytes:
    raw = settings.encryption_key
    if not raw:
        raise RuntimeError("ENCRYPTION_KEY is not configured")
    return base64.urlsafe_b64decode(raw.encode("ascii"))


def encrypt_value(plaintext: str) -> str:
    nonce = os.urandom(12)
    ciphertext = AESGCM(_key()).encrypt(nonce, plaintext.encode("utf-8"), None)
    return f"{base64.urlsafe_b64encode(nonce).decode('ascii')}.{base64.urlsafe_b64encode(ciphertext).decode('ascii')}"


def decrypt_value(stored: str) -> str:
    try:
        nonce_b64, ct_b64 = stored.split(".", 1)
        nonce = base64.urlsafe_b64decode(nonce_b64.encode("ascii"))
        ciphertext = base64.urlsafe_b64decode(ct_b64.encode("ascii"))
        plaintext = AESGCM(_key()).decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")
    except (ValueError, InvalidTag, Exception) as exc:  # noqa: BLE001
        raise ValueError("Unable to decrypt credential") from exc


def encrypt_config(config: dict) -> dict:
    """Encrypt a whole config dict for storage inside the JSONB column."""
    if not config:
        return {}
    return {_CONFIG_MARKER: encrypt_value(json.dumps(config, sort_keys=True))}


def decrypt_config(stored: dict | None) -> dict:
    """Decrypt a stored config dict; tolerates legacy plaintext rows."""
    if not stored:
        return {}
    if _CONFIG_MARKER in stored:
        try:
            raw = decrypt_value(str(stored[_CONFIG_MARKER]))
            decoded = json.loads(raw)
            return decoded if isinstance(decoded, dict) else {}
        except (ValueError, json.JSONDecodeError):
            return {}
    return dict(stored)
