import logging
import math
import os
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import UploadFile

from src.core.config import settings
from src.core.exceptions import (
    AppError,
    UploadExpiredError,
    UploadNotFoundError,
)
from src.models.upload import (
    UploadCompleteResponse,
    UploadInitiateRequest,
    UploadInitiateResponse,
    UploadSession,
    UploadStatus,
    UploadStatusResponse,
)
from src.services.azure_storage import (
    upload_file_to_azure,
)
from src.services.upload_store import upload_store

logger = logging.getLogger(__name__)


async def initiate_upload(request: UploadInitiateRequest) -> UploadInitiateResponse:
    if not os.path.isfile(request.file_path):
        raise AppError(
            message=f"File not found at path: {request.file_path}",
            code="FILE_NOT_FOUND",
            status_code=404,
        )

    max_size = settings.max_file_size_mb * 1024 * 1024
    if request.file_size > max_size:
        raise AppError(
            message=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB",
            code="FILE_TOO_LARGE",
            status_code=413,
        )

    upload_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    chunk_size = settings.azure_chunk_size_mb * 1024 * 1024
    total_parts = math.ceil(request.file_size / chunk_size)
    expiration_time = now + timedelta(hours=settings.upload_ttl_hours)

    session = UploadSession(
        upload_id=upload_id,
        file_name=request.file_name,
        file_size=request.file_size,
        file_path=request.file_path,
        destination_file_path=request.destination_file_path,
        content_type="application/octet-stream",
        status=UploadStatus.INITIATED,
        chunk_size=chunk_size,
        total_parts=total_parts,
        expiration_time=expiration_time,
        created_at=now,
    )
    upload_store.save(session)

    return UploadInitiateResponse(
        upload_id=upload_id,
        file_name=request.file_name,
        total_parts=total_parts,
        chunk_size=chunk_size,
        status=UploadStatus.INITIATED,
        created_at=now,
        expiration_time=expiration_time,
    )


async def upload_file(
    upload_id: str,
    file: UploadFile,
    metadata: dict | None = None,
) -> UploadCompleteResponse:
    file_data = await file.read()
    session = upload_store.get(upload_id)
    if not session:
        raise UploadNotFoundError(upload_id)
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(file_data) > max_size:
        raise AppError(
            message=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB",
            code="FILE_TOO_LARGE",
            status_code=413,
        )

    now = datetime.now(UTC)
    if now > session.expiration_time:
        raise UploadExpiredError(upload_id)

    container_name, blob_path = session.destination_file_path.split("/", 1)

    blob_url, blob_name, total_parts = upload_file_to_azure(
        data=file_data,
        container_name=container_name,
        blob_path=blob_path,
        file_name=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
    )

    # session = UploadSession(
    #     upload_id=upload_id,
    #     file_name=file.filename or "unknown",
    #     file_size=len(file_data),
    #     content_type=file.content_type or "application/octet-stream",
    #     status=UploadStatus.COMPLETED,
    #     blob_url=blob_url,
    #     blob_name=blob_name,
    #     metadata=metadata or {},
    #     created_at=now,
    #     completed_at=now,
    # )

    session.status = UploadStatus.COMPLETED
    session.blob_url = blob_url
    session.blob_name = blob_name
    session.completed_at = now
    if metadata:
        session.metadata = metadata

    upload_store.save(session)

    return UploadCompleteResponse(
        upload_id=upload_id,
        file_name=session.file_name,
        file_size=session.file_size,
        total_parts=total_parts,
        blob_url=blob_url,
        status=UploadStatus.COMPLETED,
        created_at=now,
        completed_at=now,
    )


async def get_upload_status(upload_id: str) -> UploadStatusResponse:
    session = upload_store.get(upload_id)
    if not session:
        raise UploadNotFoundError(upload_id)

    return UploadStatusResponse(
        upload_id=session.upload_id,
        status=session.status,
    )
