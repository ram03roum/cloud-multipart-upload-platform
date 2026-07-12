from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class UploadStatus(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    DELETED = "DELETED"


class UploadInitiateRequest(BaseModel):
    file_name: str = Field(
        ..., description="Name of the file to be uploaded", min_length=1, max_length=255
    )
    file_size: int = Field(..., description="Size of the file in bytes", gt=0)
    file_path: str = Field(..., description="Local path of the file to upload")
    destination_file_path: str = Field(
        ...,
        description="Format: 'container_name/path/in/container', ex: 'uploads/videos/clip.mp4'",
    )

    @classmethod
    def validate_destination_format(cls, value: str) -> str:
        if "/" not in value:
            raise ValueError(
                "destination_file_path doit être au format 'container_name/path', "
                "ex: 'uploads/videos/clip.mp4'"
            )
        container_name, blob_path = value.split("/", 1)
        if not container_name or not blob_path:
            raise ValueError("container_name et le chemin du blob ne peuvent pas être vides")
        return value

    @property
    def container_name(self) -> str:
        return self.destination_file_path.split("/", 1)[0]

    @property
    def blob_path(self) -> str:
        return self.destination_file_path.split("/", 1)[1]


class UploadInitiateResponse(BaseModel):
    upload_id: str
    file_name: str
    total_parts: int
    chunk_size: int
    status: UploadStatus
    created_at: datetime
    expiration_time: datetime


class UploadSession(BaseModel):
    upload_id: str
    file_name: str
    file_size: int
    file_path: str = ""
    destination_file_path: str = ""
    content_type: str
    status: UploadStatus
    chunk_size: int = 0
    total_parts: int = 0
    expiration_time: datetime | None = None
    blob_url: str = ""
    blob_name: str = ""
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    completed_at: datetime | None = None


class UploadCompleteResponse(BaseModel):
    upload_id: str
    file_name: str
    file_size: int
    status: UploadStatus
    total_parts: int
    blob_url: str
    created_at: datetime
    completed_at: datetime


class UploadStatusResponse(BaseModel):
    upload_id: str
    status: UploadStatus
