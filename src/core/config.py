from pydantic import BaseSettings, PostgresDsn, HttpUrl
from logging import config as logging_config

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    app_title: str = "File storage"
    database_dsn: PostgresDsn
    project_host: str = '0.0.0.0'
    project_port: int = 8080
    echo_queries: bool = False
    token_lifetime: int = 600  # seconds
    jwt_secret: str = 'secret_word'
    jwt_algorithm: str = 'HS256'
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    s3_endpoint: HttpUrl = 'https://storage.yandexcloud.net/'
    s3_bucket: str

    class Config:
        env_file = '.env'


app_settings = AppSettings()
