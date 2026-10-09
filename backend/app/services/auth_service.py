from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.auth.security import hash_password, verify_password
from app.auth.tokens import create_access_token
from app.config import settings
from app.models.user import Role, User
from app.repositories.tenant_repo import TenantRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def register_tenant_and_owner(db: Session, payload: RegisterRequest) -> User:
    tenant_repo = TenantRepository(db)
    if tenant_repo.get_by_slug(payload.tenant_slug) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tenant slug '{payload.tenant_slug}' is already taken")

    tenant = tenant_repo.create(slug=payload.tenant_slug, name=payload.tenant_name)
    user_repo = UserRepository(db, tenant.id)
    return user_repo.create(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=Role.OWNER,
        is_active=True,
    )


def authenticate(db: Session, payload: LoginRequest) -> TokenResponse:
    tenant_repo = TenantRepository(db)
    tenant = tenant_repo.get_by_slug(payload.tenant_slug)
    invalid_credentials = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid tenant slug, email, or password")
    if tenant is None:
        raise invalid_credentials

    user_repo = UserRepository(db, tenant.id)
    user = user_repo.get_by_email(payload.email)
    if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise invalid_credentials

    token = create_access_token(user_id=user.id, tenant_id=tenant.id, role=user.role.value)
    return TokenResponse(access_token=token, expires_in_minutes=settings.jwt_expire_minutes)
