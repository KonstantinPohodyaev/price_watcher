from sqlalchemy.ext.asyncio import AsyncSession

from src.models.price_history import PriceHistory
from src.crud.base import CRUDBase


class PriceHisstoryCRUD(CRUDBase[PriceHistory])