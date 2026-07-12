from sqlalchemy import JSON, Column, DateTime, Integer, String

from src.core.database import Base


class UploadSessionDB(Base):
    __tablename__ = "upload_sessions"

    upload_id = Column(String, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    destination_file_path = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    chunk_size = Column(Integer, default=0)
    total_parts = Column(Integer, default=0)
    expiration_time = Column(DateTime(timezone=True), nullable=True)
    blob_url = Column(String, default="")
    blob_name = Column(String, default="")
    session_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
