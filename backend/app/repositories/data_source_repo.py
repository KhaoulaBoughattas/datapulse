from app.models.data_source import DataSource
from app.repositories.base import TenantScopedRepository


class DataSourceRepository(TenantScopedRepository[DataSource]):
    model = DataSource
