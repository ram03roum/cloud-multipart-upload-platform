from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class UploadStatus(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class UploadInitiateRequest(BaseModel):
    file_name: str = Field(
        ..., description="Name of the file to be uploaded", min_length=1, max_length=255
    )
    file_size: int = Field(..., description="Size of the file in bytes", gt=0)
    content_type: str = Field(default="application/octet-stream")
    chunk_size: int = Field(description="Size of each chunk in bytes")

    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        min_size = 5 * 1024 * 1024  # 5 MB
        max_size = 100 * 1024 * 1024  # 100 MB
        if value < min_size or value > max_size:
            raise ValueError(f"Chunk size must be between {min_size} and {max_size} bytes")
        return value


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
    filename: str
    file_size: int
    content_type: str
    chunk_size: int
    total_parts: int
    metadata: dict
    status: UploadStatus
    created_at: datetime
    expiration_time: datetime
    uploaded_parts: dict[int, str] = Field(default_factory=dict)
    # clé = part_number, valeur = block_id correspondant à ce part_number dans Azure Blob Storage


class ChunkUploadResponse(BaseModel):
    upload_id: str
    part_number: int
    block_id: str
    status: str
    uploaded_parts: int
    total_parts: int
