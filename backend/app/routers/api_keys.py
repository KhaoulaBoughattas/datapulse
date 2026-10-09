from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.api_keys import generate_api_key
from app.auth.rbac import require_permission
from app.database import get_db
from app.models.user import User
from app.repositories.api_key_repo import ApiKeyRepository
from app.schemas.api_key import ApiKeyCreateRequest, ApiKeyCreateResponse, ApiKeyResponse

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("", response_model=list[ApiKeyResponse])
def list_api_keys(current_user: User = Depends(require_permission("data_source:write")), db: Session = Depends(get_db)):
    return ApiKeyRepository(db, current_user.tenant_id).list()


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(payload: ApiKeyCreateRequest, current_user: User = Depends(require_permission("data_source:write")), db: Session = Depends(get_db)):
    raw_key, key_prefix, key_hash = generate_api_key()
    repo = ApiKeyRepository(db, current_user.tenant_id)
    record = repo.create(name=payload.name, key_prefix=key_prefix, key_hash=key_hash)
    return ApiKeyCreateResponse(id=record.id, name=record.name, raw_key=raw_key, key_prefix=key_prefix, created_at=record.created_at)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(key_id: UUID, current_user: User = Depends(require_permission("data_source:write")), db: Session = Depends(get_db)):
    repo = ApiKeyRepository(db, current_user.tenant_id)
    record = repo.get(key_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    record.revoked_at = datetime.now(timezone.utc)
    db.commit()
