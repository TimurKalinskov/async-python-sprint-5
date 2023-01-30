import time
import jwt
from uuid import UUID
from fastapi import Request

from core.config import app_settings


def token_response(token: str):
    return {
        'access_token': token
    }


def sign_jwt(user_id: UUID, username: str) -> dict[str, str]:
    payload = {
        'user_id': str(user_id),
        'username': username,
        'expires': time.time() + app_settings.token_lifetime
    }
    token = jwt.encode(
        payload, app_settings.jwt_secret, algorithm=app_settings.jwt_algorithm
    )
    return token_response(token)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token,
            app_settings.jwt_secret,
            algorithms=[app_settings.jwt_algorithm]
        )
        return decoded_token if decoded_token['expires'] >= time.time() else {}
    except jwt.exceptions.DecodeError:
        return {}


def get_user_id(request: Request) -> str | None:
    token = request.headers.get('authorization')
    try:
        token = token.split()[1]
    except AttributeError:
        return None
    return decode_jwt(token).get('user_id')
