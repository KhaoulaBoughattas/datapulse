"""API key generation and verification — Argon2-hashed, prefix-indexed,
raw value shown exactly once at creation."""
from __future__ import annotations
import secrets
from app.auth.security import hash_password, verify_password

KEY_PREFIX_LENGTH = 12
KEY_TOTAL_RANDOM_CHARS = 32


def generate_api_key() -> tuple[str, str, str]:
    raw_suffix = secrets.token_urlsafe(KEY_TOTAL_RANDOM_CHARS)
    raw_key = f"dp_live_{raw_suffix}"
    key_prefix = raw_key[:KEY_PREFIX_LENGTH]
    key_hash = hash_password(raw_key)
    return raw_key, key_prefix, key_hash


def verify_api_key_value(raw_key: str, stored_hash: str) -> bool:
    return verify_password(raw_key, stored_hash)
