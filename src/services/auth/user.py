from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import select

from models.user import User
from schemas.user import UserLogin, UserUpdatePassword
from services.base import RepositoryDB
from services.exceptions import CreateException
from services.auth.utils import get_password_hash, verify_password


class RepositoryShort(RepositoryDB[User, UserLogin, UserUpdatePassword]):
    async def create(self, db: AsyncSession, *, obj_in: UserLogin) -> User:
        obj_in.password = get_password_hash(obj_in.password)
        try:
            return await super().create(db=db, obj_in=obj_in)
        except IntegrityError:
            raise CreateException

    async def get(
            self, db: AsyncSession, pk: UUID | None, username: str | None = None
    ) -> User | None:
        if pk:
            statement = select(User).where(User.id == pk)
        else:
            statement = select(User).where(User.username == username)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    @staticmethod
    async def check_user(db: AsyncSession, data_in: UserLogin) -> bool:
        statement = select(User).where(
            User.username == data_in.username,
        )
        result = await db.execute(statement=statement)
        user = result.scalar_one_or_none()
        if not user:
            raise NoResultFound
        return verify_password(data_in.password, user.password)

    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: User,
            obj_in: UserUpdatePassword | dict[str, Any]
    ) -> User:
        obj_in.password = get_password_hash(obj_in.password)
        return await super().update(db=db, db_obj=db_obj, obj_in=obj_in)


user_crud = RepositoryShort(User)
