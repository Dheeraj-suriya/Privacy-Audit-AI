"""File handling utilities with security validations."""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException

from ..core.config import settings
from ..core.logging import logger

ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS
ALLOWED_MIME_TYPES = settings.ALLOWED_MIME_TYPES
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """Validate uploaded file for security."""
    # Check filename for path traversal
    filename = Path(file.filename).name
    if ".." in filename or "/" in filename or "\\" in filename:
        return False, "Invalid filename"

    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not allowed"

    # Check MIME type
    content_type = file.content_type or ""
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        # Some browsers send generic types, be lenient but log
        logger.warning(f"Unexpected MIME type: {content_type} for {filename}")

    return True, None

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def generate_secure_filename(original: str) -> str:
    """Generate a secure internal filename."""
    ext = Path(original).suffix.lower()
    timestamp = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    return f"{timestamp}{ext}"

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage."""
    # Remove path components and dangerous characters
    name = Path(filename).name
    # Keep only safe characters
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    sanitized = "".join(c if c in safe_chars else "_" for c in name)
    return sanitized

def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = Path(filename).suffix.lower()
    type_map = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".xlsx": "xlsx",
        ".csv": "csv",
        ".txt": "txt",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
    }
    return type_map.get(ext, "unknown")
