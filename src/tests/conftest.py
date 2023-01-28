import pytest
import pytest_asyncio
import asyncio

from _pytest.monkeypatch import MonkeyPatch
from typing import AsyncGenerator, Generator
from asyncio import AbstractEventLoop
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncConnection, AsyncEngine, AsyncSession, AsyncTransaction
)
from httpx import AsyncClient

from core.config import app_settings
from db.db import Base
from tests.db_utils import create_db
from main import app


app_settings.database_dsn = f'{app_settings.database_dsn}_test'


@pytest.fixture(scope='function')
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function', autouse=True)
async def _create_db() -> None:
    await create_db(url=app_settings.database_dsn, base=Base)


@pytest_asyncio.fixture()
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine_ = create_async_engine(app_settings.database_dsn, future=True)
    try:
        yield engine_
    finally:
        await engine_.dispose()


@pytest_asyncio.fixture()
async def db_connection(
        engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture(autouse=True)
async def db_transaction(
        db_connection: AsyncConnection
) -> AsyncGenerator[AsyncTransaction, None]:
    """
    Recipe for using transaction rollback in tests
    https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites  # noqa
    """
    async with db_connection.begin() as transaction:
        yield transaction
        await transaction.rollback()


@pytest_asyncio.fixture(autouse=True)
async def session(
        db_connection: AsyncConnection, monkeypatch: MonkeyPatch
) -> AsyncGenerator[AsyncSession, None]:
    session_maker = sessionmaker(
        db_connection, class_=AsyncSession, expire_on_commit=False
    )
    monkeypatch.setattr('db.db.async_session', session_maker)

    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client
