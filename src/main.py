from fastapi import FastAPI

from src.api.health import router as health_router
from src.api.uploads import router as uploads_router
from src.core.config import settings
from src.core.exceptions import AppError, app_error_handler

app = FastAPI(title="Multipart Upload Platform", version=settings.app_version)

app.include_router(health_router)
app.include_router(uploads_router)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, app_error_handler)
