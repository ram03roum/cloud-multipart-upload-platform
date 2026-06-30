import math
import uuid
from datetime import UTC, datetime, timedelta

from src.core.config import settings
from src.models.upload import (
    UploadInitiateRequest,
    UploadInitiateResponse,
    UploadSession,
    UploadStatus,
)
from src.services.upload_store import upload_store


def initiate_upload(request: UploadInitiateRequest) -> UploadInitiateResponse:
    upload_id = str(uuid.uuid4())
    tatal_parts = math.ceil(request.file_size / request.chunk_size)
    now = datetime.now(UTC)
    expiration_time = now + timedelta(hours=settings.upload_ttl_hours)
    upload_session = UploadSession(
        upload_id=upload_id,
        filename=request.file_name,
        file_size=request.file_size,
        content_type=request.content_type,
        chunk_size=request.chunk_size,
        total_parts=tatal_parts,
        metadata={},
        status=UploadStatus.INITIATED,
        created_at=now,
        expiration_time=expiration_time,
    )
    upload_store.save(upload_session)
    return UploadInitiateResponse(
        upload_id=upload_id,
        file_name=request.file_name,
        total_parts=tatal_parts,
        chunk_size=request.chunk_size,
        status=UploadStatus.INITIATED,
        created_at=now,
        expiration_time=expiration_time,
    )
