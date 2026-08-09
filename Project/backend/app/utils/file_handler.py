import os
import re
import uuid
from typing import Tuple
from fastapi import UploadFile, HTTPException, status

# Directory where uploaded resume files will be stored
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "resumes"))

# Maximum allowed file size (5 MB)
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

# Allowed mime types & extensions
ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}


def ensure_upload_dir_exists():
    """
    Ensures the target uploads directory structure exists on disk.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filename by stripping non-alphanumeric characters (except dots and hyphens)
    to eliminate directory traversal vectors.
    """
    base_name = os.path.basename(filename)
    clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", base_name)
    return clean_name


def validate_pdf_file(file: UploadFile, contents: bytes) -> None:
    """
    Validates that the uploaded file is strictly a PDF, within max size limits,
    and contains valid PDF magic header bytes (%PDF).
    """
    # 1. Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}'. Only PDF files (.pdf) are allowed."
        )

    # 2. Validate MIME type
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{file.content_type}'. Only application/pdf is permitted."
        )

    # 3. Validate File Size
    size = len(contents)
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )
    if size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File size exceeds maximum permitted limit of 5 MB (Uploaded: {size / (1024*1024):.2f} MB)."
        )

    # 4. Check PDF Magic Header (%PDF-)
    if not contents.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File header validation failed. The file is not a valid PDF document."
        )


def save_resume_file(user_id: int, file: UploadFile, contents: bytes) -> Tuple[str, str]:
    """
    Saves the validated PDF file to disk with a secure, unique filename.
    Returns a tuple of (unique_filename, absolute_filepath).
    """
    ensure_upload_dir_exists()
    
    clean_name = sanitize_filename(file.filename or "resume.pdf")
    unique_prefix = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
    secure_filename = f"{unique_prefix}_{clean_name}"
    
    absolute_filepath = os.path.join(UPLOAD_DIR, secure_filename)
    
    with open(absolute_filepath, "wb") as f:
        f.write(contents)
        
    return secure_filename, absolute_filepath


def delete_resume_file(filename: str) -> bool:
    """
    Deletes a specified resume file from the uploads directory.
    """
    if not filename:
        return False
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False
    return False
