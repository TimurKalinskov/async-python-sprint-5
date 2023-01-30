from aiobotocore.session import AioBaseClient

from core.config import app_settings
from services.exceptions import DownloadException


async def download_content(client: AioBaseClient, file_path: str):
    # get object from s3
    response = await client.get_object(
        Bucket=app_settings.s3_bucket, Key=file_path
    )
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise DownloadException

    return response['Body'].iter_chunks()
