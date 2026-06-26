from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    app_version: str = "1.0.0"

    azure_storage_connection_string: str = ""
    azure_container_name: str = "uploads"
    max_file_size_mb: int = 5120
    chunk_size_mb: int = 16

    class Config:
        env_file = ".env"


settings = Settings()
