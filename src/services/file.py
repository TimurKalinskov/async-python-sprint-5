from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update as sqlalchemy_update
from sqlalchemy.orm import defer
from sqlalchemy.exc import IntegrityError

from models.file import File
from schemas.file import FileCreate


async def add_file_db_record(db: AsyncSession, *, obj_in: FileCreate) -> File:
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = File(**obj_in_data)
    db.add(db_obj)
    try:
        await db.commit()
        await db.refresh(db_obj)
    except IntegrityError:
        # if file already exists
        await db.rollback()
        obj_in_data['created_at'] = datetime.utcnow()
        query = (
            sqlalchemy_update(File)
            .where(File.path == db_obj.path)
            .values(**obj_in_data)
            .execution_options(synchronize_session='fetch')
        )
        await db.execute(query)
        await db.commit()
        statement = select(File).where(File.path == str(obj_in.path))
        result = await db.execute(statement=statement)
        db_obj = result.scalar_one()
    return db_obj


async def get_all_files(
        db: AsyncSession, *, user_id: str, skip=0, limit=100
) -> list[File]:
    statement = (
        select(File).
        where(File.account_id == user_id).
        options(defer(File.account_id)).
        offset(skip).
        limit(limit)
    )
    results = await db.execute(statement=statement)
    return results.scalars().all()


async def get_file_by_uuid(db: AsyncSession, pk: str, user_id=str) -> File:
    statement = (
        select(File).
        where(and_(File.id == pk, File.account_id == user_id))
    )
    result = await db.execute(statement=statement)
    return result.scalar_one_or_none()


async def get_file_by_path(db: AsyncSession, path: str, user_id=str) -> File:
    statement = (
        select(File).
        where(and_(File.path == path, File.account_id == user_id))
    )
    result = await db.execute(statement=statement)
    return result.scalar_one_or_none()


async def get_all_by_path(
        db: AsyncSession, path: str, user_id=str) -> list[File]:
    statement = (
        select(File).
        where(and_(File.path.like(f'{path}%'), File.account_id == user_id))
    )
    result = await db.execute(statement=statement)
    return list(result.scalars())
