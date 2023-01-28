from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy import select, update as sqlalchemy_update

from db.db import Base
from services.exceptions import CreateException


class Repository(ABC):

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(Repository,
                   Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, pk: UUID) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == pk)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip=0, limit=100
    ) -> list[ModelType]:
        statement = select(self._model).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(
            self, db: AsyncSession, *, objects_in: list[CreateSchemaType]
    ) -> list[ModelType]:
        objects_in_data = jsonable_encoder(objects_in)
        db_objects = [
            self._model(**obj) for obj in objects_in_data
        ]
        db.add_all(db_objects)
        try:
            await db.commit()
        except IntegrityError:
            raise CreateException
        [await db.refresh(obj) for obj in db_objects]
        return db_objects

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        query = (
            sqlalchemy_update(self._model)
            .where(self._model.id == db_obj.id)
            .values(**obj_in_data)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, pk: UUID) -> None:
        obj = await self.get(db=db, pk=pk)
        if not obj:
            raise NoResultFound
        await db.delete(obj)
        await db.commit()
