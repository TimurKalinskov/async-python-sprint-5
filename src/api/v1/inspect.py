import time
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from asyncpg.exceptions import PostgresError
from aiobotocore.session import AioBaseClient

from core.config import app_settings
from core.s3 import get_s3_client
from db.db import get_session
from schemas.inspect import Ping, DatabaseStatus, S3Status, Status
from services.auth.auth_bearer import JWTBearer


router = APIRouter()


@router.get(
    '/ping',
    response_model=Ping,
    description='Get connection time to services and get info.',
    dependencies=[Depends(JWTBearer())]
)
async def ping_services(
        db: AsyncSession = Depends(get_session),
        s3_client: AioBaseClient = Depends(get_s3_client)
) -> Any:
    """
    Ping services
    """
    db_connected = True
    s3_connected = True
    db_info = ''
    db_time = 0

    # ping database
    try:
        bd_start = time.time()
        ping = await db.execute(text('SELECT version()'))
        db_time = time.time() - bd_start
        db_info = ping.scalar_one_or_none()
    except (PostgresError, ConnectionRefusedError, TimeoutError):
        db_connected = False

    # ping file storage
    s3_start = time.time()
    resp = await s3_client.get_object_acl(
        Bucket=app_settings.s3_bucket, Key='for_ping.txt'
    )
    s3_time = time.time() - s3_start
    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        s3_connected = False

    return Ping(
        database=DatabaseStatus(
            status=Status.connected.value
            if db_connected else Status.error.value,
            info=db_info,
            time=db_time
        ),
        file_storage=S3Status(
            status=Status.connected.value
            if s3_connected else Status.error.value,
            bucket=app_settings.s3_bucket,
            base_url=app_settings.s3_endpoint,
            time=s3_time
        )
    )
