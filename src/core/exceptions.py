from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


class UploadNotFoundError(AppError):
    def __init__(self, upload_id: str):
        super().__init__(f"Upload session with ID '{upload_id}' not found.", status_code=404)


class UploadExpiredError(AppError):
    def __init__(self, upload_id: str):
        super().__init__(f"Upload session with ID '{upload_id}' has expired.", status_code=410)


class UploadAlreadyCompletedError(AppError):
    def __init__(self, upload_id: str):
        super().__init__(
            f"Upload session with ID '{upload_id}' has already been completed.", status_code=409
        )


class ChunkTooLargeError(AppError):
    def __init__(self, chunk_size: int, max_size: int):
        super().__init__(
            message=f"Chunk size {chunk_size} exceeds maximum allowed size {max_size}",
            code="CHUNK_TOO_LARGE",
            status_code=413,
        )


class InvalidPartNumberError(AppError):
    def __init__(self, part_number: int, total_parts: int):
        super().__init__(
            message=f"Part number {part_number} is invalid. Must be between 1 and {total_parts}",
            code="INVALID_PART_NUMBER",
            status_code=422,
        )


class ChecksumMismatchError(AppError):
    def __init__(self) -> None:
        super().__init__(
            message="Chunk checksum does not match provided X-Chunk-Checksum header",
            code="CHECKSUM_MISMATCH",
            status_code=422,
        )


class MissingPartsError(AppError):
    def __init__(self, missing_parts: list[int]):
        super().__init__(
            message=f"Missing parts: {missing_parts}. Upload all parts before completing.",
            code="MISSING_PARTS",
            status_code=400,
        )


class BlobChecksumMismatchError(AppError):
    def __init__(self) -> None:
        super().__init__(
            message="Final blob checksum does not match provided checksum",
            code="BLOB_CHECKSUM_MISMATCH",
            status_code=422,
        )


class UploadAlreadyDeletedError(AppError):
    def __init__(self, upload_id: str):
        super().__init__(
            message=f"Upload session '{upload_id}' is already aborted",
            code="UPLOAD_ALREADY_ABORTED",
            status_code=409,
        )
