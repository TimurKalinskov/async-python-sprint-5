import time
import jwt

from core.config import app_settings


def token_response(token: str):
    return {
        'access_token': token
    }


def sign_jwt(username: str) -> dict[str, str]:
    payload = {
        'user_id': username,
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
