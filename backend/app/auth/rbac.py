from collections.abc import Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db, set_rls_tenant_context
from app.models.user import Role, User

ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.OWNER: {"*"},
    Role.ADMIN: {
        "user:read", "user:write", "pipeline:read", "pipeline:write",
        "data_source:read", "data_source:write", "dataset:read",
        "quality:read", "quality:write",
    },
    Role.DATA_ENGINEER: {
        "pipeline:read", "pipeline:write", "data_source:read", "data_source:write",
        "dataset:read", "quality:read", "quality:write",
    },
    Role.ANALYST: {"pipeline:read", "data_source:read", "dataset:read", "quality:read"},
    Role.VIEWER: {"pipeline:read", "dataset:read", "quality:read"},
}


def require_permission(permission: str) -> Callable[..., User]:
    def dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        allowed = ROLE_PERMISSIONS.get(current_user.role, set())
        if "*" not in allowed and permission not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{current_user.role.value}' lacks permission '{permission}'")
        set_rls_tenant_context(db, current_user.tenant_id)
        return current_user

    return dependency
