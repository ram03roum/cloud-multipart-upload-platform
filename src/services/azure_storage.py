import base64

from azure.storage.blob import BlobServiceClient

from src.core.config import settings


def get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)


def generate_block_id(part_number: int) -> str:
    """
    Generate a unique block ID for the given part number.

    Args:
        part_number (int): The part number for which to generate the block ID.
    """
    raw = f"{part_number:05d}"
    return base64.b64encode(raw.encode()).decode()


def stage_block(upload_id: str, block_id: str, data: bytes) -> None:
    client = get_blob_service_client()
    blob_client = client.get_blob_client(
        container=settings.azure_container_name,
        blob=upload_id,
    )

    blob_client.stage_block(
        block_id=block_id,
        data=data,
    )
