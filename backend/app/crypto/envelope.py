"""Envelope encryption for data_sources.connection_config. Uses Fernet
(AES-128-CBC + HMAC) with a single data-encryption key from config."""
from __future__ import annotations
import json
from typing import Any
from cryptography.fernet import Fernet, InvalidToken
from app.config import settings


def _fernet() -> Fernet:
    return Fernet(settings.data_encryption_key.encode())


def encrypt_dict(data: dict[str, Any]) -> bytes:
    plaintext = json.dumps(data).encode("utf-8")
    return _fernet().encrypt(plaintext)


def decrypt_dict(ciphertext: bytes) -> dict[str, Any]:
    try:
        plaintext = _fernet().decrypt(ciphertext)
    except InvalidToken as exc:
        raise ValueError("Could not decrypt connection_config — DATA_ENCRYPTION_KEY may have changed.") from exc
    return json.loads(plaintext)
