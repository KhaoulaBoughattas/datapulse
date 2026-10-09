from app.models.dataset import Dataset
from app.repositories.base import TenantScopedRepository


class DatasetRepository(TenantScopedRepository[Dataset]):
    model = Dataset
