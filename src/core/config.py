from pydantic import BaseSettings, PostgresDsn
from logging import config as logging_config

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    app_title: str = "URLs shorts"
    database_dsn: PostgresDsn
    project_host: str = '0.0.0.0'
    project_port: int = 8080
    length_url: int = 6
    domain_prefix: str = ''  # for example, 'test.ru/'
    echo_queries: bool = False

    class Config:
        env_file = '.env'


app_settings = AppSettings()
