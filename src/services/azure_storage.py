import base64

from azure.storage.blob import BlobBlock, BlobServiceClient, ContentSettings

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


def commit_block_list(
    upload_id: str,
    block_ids: list[str],
    metadata: dict,
    content_type: str,
) -> str:
    client = get_blob_service_client()
    blob_client = client.get_blob_client(
        container=settings.azure_container_name,
        blob=upload_id,
    )

    block_list = [BlobBlock(block_id=block_id) for block_id in block_ids]

    blob_client.commit_block_list(
        block_list=block_list,
        metadata=metadata,
        content_settings=ContentSettings(content_type=content_type),
    )

    return blob_client.url


def get_blob_checksum(upload_id: str) -> str:
    client = get_blob_service_client()
    blob_client = client.get_blob_client(
        container=settings.azure_container_name,
        blob=upload_id,
    )
    properties = blob_client.get_blob_properties()
    return properties.get("content_settings", {}).get("content_md5", "")
