from datetime import datetime
from uuid import UUID
from pathlib import Path

from pydantic import BaseModel, constr
from fastapi import Form


class FileInfo(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    path: Path
    size: int
    is_downloadable: bool


class FileInDBBase(FileInfo):
    account_id: UUID
    content_type: str

    class Config:
        orm_mode = True


class FileCreate(BaseModel):
    name: str
    path: Path
    size: int
    is_downloadable: bool
    account_id: UUID
    content_type: str


class FileDownloaded(BaseModel):
    account_id: UUID
    files: list[FileInfo]
