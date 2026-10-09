"""FastAPI dependencies verifying either a JWT (interactive users) or an
API key (automation). Both resolve to the same User object."""
from typing import Annotated
from uuid import UUID
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.api_keys import verify_api_key_value
from app.config import settings
from app.database import get_db
from app.models.api_key import ApiKey
from app.models.user import User

bearer_scheme = HTTPBearer()

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _try_jwt(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    user = db.get(User, UUID(user_id))
    if user is None or not user.is_active:
        return None
    return user


def _try_api_key(raw_key: str, db: Session) -> User | None:
    """API keys authenticate as the tenant's OWNER user — a known,
    stated limitation (not yet scoped independently of a user's role)."""
    if not raw_key.startswith("dp_live_"):
        return None
    prefix = raw_key[:12]
    candidates = db.scalars(select(ApiKey).where(ApiKey.key_prefix == prefix, ApiKey.revoked_at.is_(None))).all()
    for candidate in candidates:
        if verify_api_key_value(raw_key, candidate.key_hash):
            from datetime import datetime, timezone
            candidate.last_used_at = datetime.now(timezone.utc)
            db.commit()
            owner = db.scalars(select(User).where(User.tenant_id == candidate.tenant_id, User.role == "OWNER")).first()
            return owner
    return None


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    token = credentials.credentials
    user = _try_api_key(token, db) if token.startswith("dp_live_") else _try_jwt(token, db)
    if user is None:
        raise _credentials_exception
    return user
