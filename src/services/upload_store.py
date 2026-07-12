from src.core.database import SessionLocal
from src.models.db_models import UploadSessionDB
from src.models.upload import UploadSession


class InMemoryUploadStore:
    def __init__(self):
        self._sessions: dict[str, UploadSession] = {}

    def save(self, session: UploadSession) -> None:
        self._sessions[session.upload_id] = session

    def get(self, upload_id: str) -> UploadSession | None:
        return self._sessions.get(upload_id)

    def delete(self, upload_id: str) -> None:
        self._sessions.pop(upload_id, None)


upload_store = InMemoryUploadStore()


class UploadStore:
    def _to_pydantic(self, db_session: UploadSessionDB) -> UploadSession:
        return UploadSession(
            upload_id=db_session.upload_id,
            file_name=db_session.file_name,
            file_size=db_session.file_size,
            file_path=db_session.file_path,
            destination_file_path=db_session.destination_file_path,
            content_type=db_session.content_type,
            status=db_session.status,
            chunk_size=db_session.chunk_size,
            total_parts=db_session.total_parts,
            expiration_time=db_session.expiration_time,
            blob_url=db_session.blob_url,
            blob_name=db_session.blob_name,
            metadata=db_session.session_metadata or {},
            created_at=db_session.created_at,
            completed_at=db_session.completed_at,
        )

    def save(self, session: UploadSession) -> None:
        db = SessionLocal()
        try:
            db_obj = db.get(UploadSessionDB, session.upload_id)
            if db_obj is None:
                db_obj = UploadSessionDB(upload_id=session.upload_id)
                db.add(db_obj)

            db_obj.file_name = session.file_name
            db_obj.file_size = session.file_size
            db_obj.file_path = session.file_path
            db_obj.destination_file_path = session.destination_file_path
            db_obj.content_type = session.content_type
            db_obj.status = session.status.value
            db_obj.chunk_size = session.chunk_size
            db_obj.total_parts = session.total_parts
            db_obj.expiration_time = session.expiration_time
            db_obj.blob_url = session.blob_url
            db_obj.blob_name = session.blob_name
            db_obj.session_metadata = session.metadata
            db_obj.created_at = session.created_at
            db_obj.completed_at = session.completed_at

            db.commit()
        finally:
            db.close()

    def get(self, upload_id: str) -> UploadSession | None:
        db = SessionLocal()
        try:
            db_obj = db.get(UploadSessionDB, upload_id)
            if db_obj is None:
                return None
            return self._to_pydantic(db_obj)
        finally:
            db.close()


upload_store = UploadStore()
