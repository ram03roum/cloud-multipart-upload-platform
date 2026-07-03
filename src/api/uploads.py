from fastapi import APIRouter, Header, UploadFile, status

from src.models.upload import (
    ChunkUploadResponse,
    UploadCompleteResponse,
    UploadDeleteResponse,
    UploadInitiateRequest,
    UploadInitiateResponse,
)
from src.services.upload_service import (
    complete_upload,
    delete_upload,
    initiate_upload,
    upload_chunk,
)

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])


@router.post(
    "/initiate", response_model=UploadInitiateResponse, status_code=status.HTTP_201_CREATED
)
def inititate_upload(request: UploadInitiateRequest):
    """
    Initiate a new file upload session.
    """
    return initiate_upload(request)


@router.put(
    "/{upload_id}/parts/{part_number}",
    response_model=ChunkUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_chunk_endpoint(
    upload_id: str,
    part_number: int,
    chunk: UploadFile,
    checksum: str | None = Header(default=None),
) -> ChunkUploadResponse:
    """
    Upload a chunk of the file.
    """
    return await upload_chunk(
        upload_id=upload_id, part_number=part_number, chunk=chunk, checksum=checksum
    )


@router.post(
    "/{upload_id}/complete",
    response_model=UploadCompleteResponse,
    status_code=status.HTTP_200_OK,
)
def complete_upload_endpoint(
    upload_id: str, x_blob_checksum: str | None = Header(default=None)
) -> UploadCompleteResponse:
    return complete_upload(upload_id=upload_id, expected_checksum=x_blob_checksum)


@router.delete(
    "/{upload_id}",
    response_model=UploadDeleteResponse,
    status_code=status.HTTP_200_OK,
)
def delete_upload_endpoint(upload_id: str) -> UploadDeleteResponse:
    """
    Delete an upload session.
    """
    return delete_upload(upload_id=upload_id)
