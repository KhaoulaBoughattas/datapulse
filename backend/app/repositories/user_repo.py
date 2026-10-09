from sqlalchemy import select
from app.models.user import User
from app.repositories.base import TenantScopedRepository


class UserRepository(TenantScopedRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.tenant_id == self.tenant_id, User.email == email)
        return self.db.scalars(stmt).first()
