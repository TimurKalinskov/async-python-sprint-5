import os
from typing import Any
from uuid import UUID
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from pydantic import constr
from sqlalchemy.ext.asyncio import AsyncSession
from aiobotocore.session import AioBaseClient
from fastapi import (
    APIRouter, Depends, HTTPException, status, Request, Query, Form, UploadFile
)

from core.s3 import get_s3_client
from db.db import get_session
from schemas import file as file_schema
from services.auth.auth_bearer import JWTBearer
from services.auth.auth_handler import get_user_id
from services.exceptions import UploadException, DownloadException
from services.s3_files.upload import upload_content
from services.s3_files.download import download_content
from services.utils import is_valid_uuid, translit
from services.file import (
    add_file_db_record, get_all_files, get_file_by_uuid, get_file_by_path
)

router = APIRouter()


@router.get(
    '/list',
    response_model=file_schema.FileDownloaded,
    summary='Get a list of URLs',
    description='Get a list of URLs and their shorthand representation.',
    dependencies=[Depends(JWTBearer())]
)
async def get_list_files(
        request: Request,
        db: AsyncSession = Depends(get_session),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=0)
) -> Any:
    """
    Retrieve list of files.
    """
    user_id = get_user_id(request)
    files = await get_all_files(db=db, user_id=user_id, skip=skip, limit=limit)

    files_dict = jsonable_encoder(files)
    files = []
    if files_dict:
        files = [file_schema.FileInfo(**file) for file in files_dict]
    result = file_schema.FileDownloaded(
        account_id=user_id,
        files=files
    )
    return result


@router.post(
    '/upload',
    status_code=status.HTTP_201_CREATED,
    response_model=file_schema.FileInDBBase,
    summary='Create short URL',
    description='Create new shorthand representation by URL.',
    dependencies=[Depends(JWTBearer())]
)
async def upload_file(
        *,
        request: Request,
        db: AsyncSession = Depends(get_session),
        path: constr(regex=r'^[^\/].+(?=\/)*[\/]?.+$') = Form(...),
        file_bytes: UploadFile,
        s3_client: AioBaseClient = Depends(get_s3_client)
) -> Any:
    """
    Upload new file.
    """
    if path[-1] == '/':
        path = os.path.join(path, file_bytes.filename)

    file_size = len(await file_bytes.read())
    await file_bytes.seek(0)

    object_in = file_schema.FileCreate(
            name=Path(path).name,
            path=path,
            size=file_size,
            is_downloadable=True,
            account_id=get_user_id(request),
            content_type=file_bytes.content_type
    )
    try:
        await upload_content(
            client=s3_client, content=await file_bytes.read(), file_path=path
        )
    except UploadException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='S3 upload error'
        )
    file_object = await add_file_db_record(db=db, obj_in=object_in)

    return file_object


@router.get(
    '/download',
    status_code=status.HTTP_200_OK,
    response_class=StreamingResponse,
    summary='Create short URL',
    description='Create new shorthand representation by URL.',
    dependencies=[Depends(JWTBearer())]
)
async def download_file(
        *,
        request: Request,
        db: AsyncSession = Depends(get_session),
        path: constr(regex=r'^[^\/].+(?=\/)*[\/]?.+$') | UUID =
        Query(..., description='Path or UUID4'),
        s3_client: AioBaseClient = Depends(get_s3_client)
) -> Any:
    """
    Download file.
    """
    user_id = get_user_id(request)

    if is_valid_uuid(path):
        file_obj = await get_file_by_uuid(db=db, pk=path, user_id=user_id)
    else:
        file_obj = await get_file_by_path(db=db, path=path, user_id=user_id)
    if not file_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File with this UUID not found'
        )

    try:
        return StreamingResponse(
            await download_content(client=s3_client, file_path=file_obj.path),
            media_type=file_obj.content_type,
            headers={
                'Content-Disposition':
                    f'filename="{file_obj.name.translate(translit)}"'
            }
        )
    except DownloadException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='S3 download error'
        )
