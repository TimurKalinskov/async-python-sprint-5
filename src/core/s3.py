from aiobotocore.session import get_session, AioBaseClient

from core.config import app_settings


async def get_s3_client() -> AioBaseClient:
    session = get_session()
    async with session.create_client(
            's3',
            aws_secret_access_key=app_settings.aws_secret_access_key,
            aws_access_key_id=app_settings.aws_access_key_id,
            endpoint_url=app_settings.s3_endpoint) as client:
        yield client
