from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth.auth_handler import decode_jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials: HTTPAuthorizationCredentials = \
            await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403,
                    detail='Invalid authentication scheme.'
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail='Invalid token or expired token.'
                )
            return credentials
        else:
            raise HTTPException(
                status_code=403,
                detail='Invalid authorization code.'
            )

    @staticmethod
    def verify_jwt(jwtoken: str) -> bool:
        return bool(decode_jwt(jwtoken))
