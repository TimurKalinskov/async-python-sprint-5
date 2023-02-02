from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from db.db import get_session
from schemas.user import UserLogin, TokenJWT
from services.auth.auth_handler import sign_jwt
from services.auth.user import user_crud
from services.exceptions import CreateException


router = APIRouter()


@router.post(
    '/register',
    response_model=TokenJWT,
    description='Create new user and take access token.'
)
async def create_user(
        user_in: UserLogin, db: AsyncSession = Depends(get_session)
):
    try:
        user = await user_crud.create(db=db, obj_in=user_in)
    except CreateException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists'
        )
    return sign_jwt(user.id, user.username)


@router.post(
    '/login',
    response_model=TokenJWT,
    description='Login to get a token.'
)
async def user_login(user: UserLogin, db: AsyncSession = Depends(get_session)):
    try:
        user = await user_crud.check_user(db=db, data_in=user)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User does not exist'
        )
    if user:
        return sign_jwt(user.id, user.username)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Wrong password'
    )
