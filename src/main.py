import logging

from fastapi import FastAPI

from src.api.health import router as health_router
from src.api.uploads import router as uploads_router
from src.core.config import settings
from src.core.database import Base, engine
from src.core.exceptions import AppError, app_error_handler, unhandled_exception_handler

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("azure.storage").setLevel(logging.DEBUG)
logging.getLogger("azure.core.pipeline").setLevel(logging.DEBUG)
logging.getLogger("azure").setLevel(logging.DEBUG)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multipart Upload Platform", version=settings.app_version)

app.include_router(health_router)
app.include_router(uploads_router)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
