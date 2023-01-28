from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, AnyHttpUrl

from schemas.short import ShortUrl


class ShortUrlStatisticBase(BaseModel):
    url_short: ShortUrl
    client_host: str
    client_port: int


class ShortUrlStatisticCreate(ShortUrlStatisticBase):
    url_short: AnyHttpUrl


class ShortUrlStatisticDBBase(ShortUrlStatisticBase):
    id: UUID
    url_short: ShortUrl
    used_at: datetime
    client_host: str
    client_port: int

    class Config:
        orm_mode = True


class ShortUrlStatistic(ShortUrlStatisticDBBase):
    pass


class ShortUrlUsesCount(BaseModel):
    url_short: ShortUrl
    uses_count: int


class ShortUrlStatisticRecord(BaseModel):
    used_at: datetime
    client_host: str
    client_port: int


class ShortUrlFullStatistic(ShortUrlUsesCount):
    statistics: list[ShortUrlStatisticRecord]
