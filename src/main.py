from fastapi import FastAPI

from src.api.health import router as health_router
from src.core.config import settings

app = FastAPI(title="Multipart Upload Platform", version=settings.app_version)

app.include_router(health_router)
