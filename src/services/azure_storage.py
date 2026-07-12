import base64
import logging
import math
import uuid

from azure.storage.blob import BlobServiceClient, ContentSettings

from src.core.config import settings

logger = logging.getLogger(__name__)


def get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string,
        connection_timeout=600,
        read_timeout=600,
    )


def generate_block_id(index: int) -> str:
    raw = f"{index:05d}"
    return base64.b64encode(raw.encode()).decode()


def upload_file_to_azure(
    data: bytes,
    container_name: str,
    blob_path: str,
    file_name: str,
    content_type: str,
) -> tuple[str, str, int]:
    blob_name = f"{uuid.uuid4()}/{file_name}"
    chunk_size = settings.azure_chunk_size_mb * 1024 * 1024
    total_parts = math.ceil(len(data) / chunk_size)

    logger.info(f"Starting upload: {file_name}")
    logger.info(f"File size: {len(data) / (1024*1024):.2f} MB")
    logger.info(f"Chunk size: {settings.azure_chunk_size_mb} MB")
    logger.info(f"Total parts: {total_parts}")

    client = get_blob_service_client()
    blob_client = client.get_blob_client(
        container=container_name,
        blob=blob_path,
    )

    block_ids = []

    for i in range(total_parts):
        start = i * chunk_size
        end = min(start + chunk_size, len(data))
        chunk_data = data[start:end]

        block_id = generate_block_id(i + 1)
        blob_client.stage_block(block_id=block_id, data=chunk_data)
        block_ids.append(block_id)

        logger.info(f"Uploaded part {i + 1}/{total_parts} ({len(chunk_data) / (1024*1024):.2f} MB)")

    blob_client.commit_block_list(
        block_ids,
        content_settings=ContentSettings(content_type=content_type),
    )

    logger.info(f"Upload complete: {blob_client.url}")
    return blob_client.url, blob_name, total_parts
