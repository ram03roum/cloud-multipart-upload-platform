from fastapi import APIRouter, status

from src.models.upload import UploadInitiateRequest, UploadInitiateResponse
from src.services.upload_service import initiate_upload

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])


@router.post(
    "/initiate", response_model=UploadInitiateResponse, status_code=status.HTTP_201_CREATED
)
def inititate_upload(request: UploadInitiateRequest):
    """
    Initiate a new file upload session.
    """
    return initiate_upload(request)
