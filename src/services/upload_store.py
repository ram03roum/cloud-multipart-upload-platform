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
