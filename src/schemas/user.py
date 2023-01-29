from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, constr


class UserBase(BaseModel):
    username: constr(regex=r'^\S[a-zA-Z0-9_]+$', max_length=64)


class UserLogin(UserBase):
    password: constr(regex=r'^\S+$')

    class Config:
        schema_extra = {
            'example': {
                'username': 'user_example',
                'password': 'password123'
            }
        }


class UserInDBBase(UserBase):
    id: UUID
    created_at: datetime


class UserUpdatePassword(UserBase):
    password: constr(regex=r'^\S+$')


class TokenJWT(BaseModel):
    access_token: str
