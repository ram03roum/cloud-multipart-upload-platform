from fastapi import APIRouter, File, UploadFile, status

from src.models.upload import (
    UploadCompleteResponse,
    UploadInitiateRequest,
    UploadInitiateResponse,
    UploadStatusResponse,
)
from src.services.upload_service import (
    get_upload_status,
    initiate_upload,
    upload_file,
)

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])


@router.post(
    "/init",
    response_model=UploadInitiateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def init_upload_endpoint(
    request: UploadInitiateRequest,
) -> UploadInitiateResponse:
    return await initiate_upload(request)


@router.post(
    "/{upload_id}", response_model=UploadCompleteResponse, status_code=status.HTTP_201_CREATED
)
async def upload_endpoint(
    upload_id: str,
    file: UploadFile = File(...),
) -> UploadCompleteResponse:
    return await upload_file(upload_id, file)


@router.get(
    "/{upload_id}/status",
    response_model=UploadStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_upload_status_endpoint(upload_id: str) -> UploadStatusResponse:
    return await get_upload_status(upload_id)
