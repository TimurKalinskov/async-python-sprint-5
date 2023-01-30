from aiobotocore.session import AioBaseClient

from core.config import app_settings
from services.exceptions import UploadException


async def upload_content(
        client: AioBaseClient, content: bytes, file_path: str) -> None:
    response = await client.put_object(
        Bucket=app_settings.s3_bucket, Key=file_path, Body=content
    )
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise UploadException
