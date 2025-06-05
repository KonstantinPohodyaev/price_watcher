from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_user_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession
    ):
        """Получение пользователя по его telegram-id."""
        return (
            await session.execute(
                select(self.model).where(
                    self.model.telegram_id == telegram_id
                )
            )
        ).scalar()

    async def get_user_by_email(
        self,
        email: str,
        session: AsyncSession
    ):
        """Получение пользователя по его email."""
        return (
            await session.execute(
                select(self.model).where(
                    self.model.email == email
                )
            )
        ).scalar()


user_crud = UserCRUD(User)
