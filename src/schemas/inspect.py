from enum import Enum
from pydantic import BaseModel, Field


class Status(str, Enum):
    connected = 'connected'
    error = 'error'


class DatabaseStatusBase(BaseModel):
    info: str | None = None


class DatabaseStatusSuccess(DatabaseStatusBase):
    status: Status = Field(Status.connected.value)
    info: str | None = Field(
        title='Info about database',
        description='Database name and version'
    )


class DatabaseStatusFail(DatabaseStatusBase):
    status: Status = Field(Status.error.value)
    info: str | None = Field(
        title='Info about error'
    )
