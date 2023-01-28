from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sqlalchemy_update
from sqlalchemy.exc import NoResultFound

from services.base import RepositoryDB
from services.utils import generate_short_url
from services.exceptions import UrlDeletedException
from models.short import Short
from schemas.short import ShortUrlCreate, ShortUrlUpdate


class RepositoryShort(RepositoryDB[Short, ShortUrlCreate, ShortUrlUpdate]):

    async def create(
            self, db: AsyncSession, *, objects_in: list[ShortUrlCreate]
    ) -> list[Short]:
        for obj in objects_in:
            if not obj.url_short:
                # generation of a short url and checking it not exists in the db
                short_url = generate_short_url(obj.url)
                statement = select(Short).where(Short.url_short == short_url)
                exist_url = await db.execute(statement=statement)
                while exist_url.scalar_one_or_none():
                    short_url = generate_short_url(obj.url)
                    exist_url = await db.execute(statement=statement)
                obj.url_short = short_url

        return await super().create(db=db, objects_in=objects_in)

    async def get_multi(
        self, db: AsyncSession, *, skip=0, limit=100
    ) -> list[Short]:
        statement = (
            select(Short)
            .where(Short.deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def get(self, db: AsyncSession, pk: UUID) -> Short | None:
        results = await super().get(db=db, pk=pk)
        if not results:
            return None
        if results.deleted:
            raise UrlDeletedException
        return results

    async def delete(self, db: AsyncSession, *, pk: UUID) -> None:
        query = (
            sqlalchemy_update(Short)
            .where(Short.id == pk)
            .values(deleted=True)
            .execution_options(synchronize_session="fetch")
        )
        result = await db.execute(query)
        if result.rowcount == 0:
            raise NoResultFound
        await db.commit()


short_crud = RepositoryShort(Short)
