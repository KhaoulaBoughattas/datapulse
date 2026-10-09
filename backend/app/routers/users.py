from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.rbac import require_permission
from app.auth.security import hash_password
from app.database import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(current_user: User = Depends(require_permission("user:read")), db: Session = Depends(get_db)) -> list[User]:
    return UserRepository(db, current_user.tenant_id).list()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest, current_user: User = Depends(require_permission("user:write")), db: Session = Depends(get_db)) -> User:
    repo = UserRepository(db, current_user.tenant_id)
    if repo.get_by_email(payload.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use in this tenant")
    return repo.create(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, current_user: User = Depends(require_permission("user:read")), db: Session = Depends(get_db)) -> User:
    user = UserRepository(db, current_user.tenant_id).get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
