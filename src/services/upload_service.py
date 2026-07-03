import hashlib
import math
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import UploadFile

from src.core.config import settings
from src.core.exceptions import (
    ChecksumMismatchError,
    ChunkTooLargeError,
    InvalidPartNumberError,
    MissingPartsError,
    UploadAlreadyCompletedError,
    UploadAlreadyDeletedError,
    UploadExpiredError,
    UploadNotFoundError,
)
from src.models.upload import (
    ChunkUploadResponse,
    UploadCompleteResponse,
    UploadDeleteResponse,
    UploadInitiateRequest,
    UploadInitiateResponse,
    UploadSession,
    UploadStatus,
)
from src.services.azure_storage import (
    commit_block_list,
    generate_block_id,
    get_blob_checksum,
    stage_block,
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


async def upload_chunk(
    upload_id: str, part_number: int, chunk: UploadFile, checksum: str
) -> ChunkUploadResponse:
    # Validate the upload session
    session = upload_store.get(upload_id)
    if not session:
        raise UploadNotFoundError(upload_id)
    # Check if the upload session has expired
    if session.expiration_time < datetime.now(UTC):
        raise UploadExpiredError(upload_id)
    # Check if the upload session is already completed
    if session.status == UploadStatus.COMPLETED:
        raise UploadAlreadyCompletedError(upload_id)
    # Validate the part number
    if part_number < 1 or part_number > session.total_parts:
        raise InvalidPartNumberError(part_number, session.total_parts)
    # read the chunk data
    chunk_data = await chunk.read()
    # Validate the taille of the checksum
    max_chunk_size = session.chunk_size
    if len(chunk_data) > max_chunk_size:
        raise ChunkTooLargeError(len(chunk_data), max_chunk_size)
    # Validate the checksum
    if checksum:
        computed = hashlib.md5(chunk_data).hexdigest()
        if computed != checksum:
            raise ChecksumMismatchError()
    # Generate a block ID for Azure Blob Storage
    block_id = generate_block_id(part_number)
    stage_block(upload_id, block_id, chunk_data)
    # Update the upload session with the uploaded part
    session.uploaded_parts[part_number] = block_id
    session.status = UploadStatus.IN_PROGRESS
    upload_store.save(session)
    return ChunkUploadResponse(
        upload_id=upload_id,
        part_number=part_number,
        status=UploadStatus.IN_PROGRESS,
        uploaded_parts=len(session.uploaded_parts),
        total_parts=session.total_parts,
        block_id=block_id,
    )


def complete_upload(
    upload_id: str,
    expected_checksum: str | None = None,
) -> UploadCompleteResponse:
    # Validate the upload session
    session = upload_store.get(upload_id)
    if not session:
        raise UploadNotFoundError(upload_id)
    # Check if the upload session has expired
    if session.expiration_time < datetime.now(UTC):
        raise UploadExpiredError(upload_id)
    # Check if the upload session is already completed
    if session.status == UploadStatus.COMPLETED:
        raise UploadAlreadyCompletedError(upload_id)
    # Validate that all parts have been uploaded
    if len(session.uploaded_parts) != session.total_parts:
        raise MissingPartsError(
            missing_parts=[
                i for i in range(1, session.total_parts + 1) if i not in session.uploaded_parts
            ]
        )
    # Commit the block list to Azure Blob Storage

    block_ids = [session.uploaded_parts[i] for i in range(1, session.total_parts + 1)]
    blob_url = commit_block_list(
        upload_id=upload_id,
        block_ids=block_ids,
        metadata=session.metadata,
        content_type=session.content_type,
    )
    # Validate the final checksum if provided
    if expected_checksum:
        final_checksum = get_blob_checksum(upload_id)
        if final_checksum != expected_checksum:
            raise ChecksumMismatchError()
    # Update the upload session status to COMPLETED
    session.status = UploadStatus.COMPLETED
    upload_store.save(session)
    return UploadCompleteResponse(
        upload_id=upload_id,
        file_name=session.filename,
        status=UploadStatus.COMPLETED,
        total_parts=session.total_parts,
        blob_url=blob_url,
        completed_at=datetime.now(UTC),
    )


def delete_upload(upload_id: str) -> UploadDeleteResponse:
    # Validate the upload session
    session = upload_store.get(upload_id)
    if not session:
        raise UploadNotFoundError(upload_id)
    # Check if the upload session is already completed
    if session.status == UploadStatus.COMPLETED:
        raise UploadAlreadyCompletedError(upload_id)
    # Check if the upload session is already deleted
    if session.status == UploadStatus.DELETED:
        raise UploadAlreadyDeletedError(upload_id)
    # Mark the upload session as DELETED
    session.status = UploadStatus.DELETED
    upload_store.save(session)
    return UploadDeleteResponse(
        upload_id=upload_id,
        status=UploadStatus.DELETED,
        deleted_at=datetime.now(UTC),
    )
