from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    app_version: str = "1.0.0"

    azure_storage_connection_string: str = ""
    azure_container_name: str = "uploads"
    max_file_size_mb: int = 5120
    azure_chunk_size_mb: int = 16
    upload_ttl_hours: int = 24
    azure_max_concurrency: int = 4
    azure_connection_timeout: int = 600
    database_url: str = (
        "postgresql://dbadmin:UploadPlatform2026!@db-upload-platform.postgres.database.azure.com:5432/upload-platform?sslmode=require"
    )

    class Config:
        env_file = ".env"


settings = Settings()
