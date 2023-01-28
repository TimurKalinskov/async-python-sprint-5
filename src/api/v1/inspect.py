from typing import Any

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from asyncpg.exceptions import PostgresError

from db.db import get_session
from schemas.inspect import DatabaseStatusSuccess, DatabaseStatusFail


router = APIRouter()


@router.get(
    '/ping',
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': DatabaseStatusFail},
        status.HTTP_200_OK: {'model': DatabaseStatusSuccess}
    },
    description='Get database connection status. '
                'If the database is connected - show information about it.'
)
async def ping_database(
        response: Response, db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Get database connection status
    """
    try:
        ping = await db.execute(text('SELECT version()'))
    except (PostgresError, ConnectionRefusedError) as er:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DatabaseStatusFail(
            info=str(er)
        )
    except TimeoutError as er:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return DatabaseStatusFail(
            info='Database connection timeout'
        )
    return DatabaseStatusSuccess(
        info=ping.scalar_one_or_none()
    )
