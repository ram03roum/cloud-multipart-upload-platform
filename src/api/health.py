from fastapi import APIRouter

from src.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.app_version}
