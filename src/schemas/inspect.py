from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class Status(str, Enum):
    connected = 'connected'
    error = 'error'


class DatabaseStatus(BaseModel):
    status: Status = Field(Status.connected.value)
    info: str | None = Field(
        title='Info about database',
        description='Database name and version'
    )
    time: float = Field(description='ping time')


class S3Status(BaseModel):
    status: Status = Field(Status.connected.value)
    bucket: str
    base_url: HttpUrl
    time: float = Field(description='ping time')


class Ping(BaseModel):
    database: DatabaseStatus
    file_storage: S3Status
