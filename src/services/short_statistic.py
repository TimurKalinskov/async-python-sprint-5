from uuid import UUID
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, NoResultFound

from models.short import Short, ShortStatistic
from schemas.short import ShortUrl
from services.exceptions import (
    CreateStatisticException, UrlDeletedException
)
from schemas.short_statistic import (
    ShortUrlStatisticCreate, ShortUrlFullStatistic, ShortUrlStatisticRecord,
    ShortUrlUsesCount
)


async def get_uses_count(db: AsyncSession, pk: UUID) -> ShortUrlUsesCount:
    statement = select(
        Short.id, Short.url, Short.url_short, Short.created_at, Short.deleted,
        func.count(ShortStatistic.id).label('count')
    ).where(Short.id == pk).join(
        ShortStatistic, Short.url_short == ShortStatistic.url_short,
        isouter=True
    ).group_by(Short)

    obj = await db.execute(statement=statement)
    obj = obj.fetchone()
    if not obj:
        raise NoResultFound
    if obj.deleted:
        raise UrlDeletedException

    obj = jsonable_encoder(obj)
    return ShortUrlUsesCount(url_short=ShortUrl(**obj), uses_count=obj['count'])


async def create_statistic_record(
        db: AsyncSession, url_statistic: ShortUrlStatisticCreate) -> None:
    obj_in_data = jsonable_encoder(url_statistic)
    db_obj = ShortStatistic(**obj_in_data)
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        raise CreateStatisticException


async def get_full_statistic(
        db: AsyncSession, pk: UUID, skip=0, limit=100
) -> ShortUrlFullStatistic:

    count_query = select(
        func.count(ShortStatistic.id).label('uses_count')
    ).join(
        Short, Short.url_short == ShortStatistic.url_short).where(
        Short.id == pk)
    # get Short object, statistic and count of uses
    statement = select(
        Short.id, Short.url, Short.url_short, Short.created_at, Short.deleted,
        ShortStatistic.used_at, ShortStatistic.client_host,
        ShortStatistic.client_port, count_query.c.uses_count
    ).where(Short.id == pk).join(
        ShortStatistic, Short.url_short == ShortStatistic.url_short,
        isouter=True
    ).offset(skip).limit(limit)

    result = await db.execute(statement=statement)
    result = jsonable_encoder(result.all())

    if not result:
        raise NoResultFound
    if result[0]['deleted']:
        raise UrlDeletedException

    uses_count = result[0]['uses_count']

    statistics = []
    if uses_count != 0:
        statistics = [ShortUrlStatisticRecord(**stat) for stat in result]

    return ShortUrlFullStatistic(
        url_short=ShortUrl(**result[0]),
        uses_count=uses_count,
        statistics=statistics
    )
