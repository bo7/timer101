"""
File upload endpoints
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Upload directory
UPLOAD_DIR = Path("/home/user/timer101/backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/picture")
async def upload_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a picture for a worktime entry.
    Returns the filename to be stored in the database.
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": unique_filename,
        "size": file_size,
        "content_type": file.content_type
    }


@router.get("/picture/{filename}")
async def get_picture(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve an uploaded picture.
    """
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Picture not found")

    return FileResponse(file_path)


@router.delete("/picture/{filename}")
async def delete_picture(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an uploaded picture.
    """
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Picture not found")

    # Delete file
    os.remove(file_path)

    return {"message": "Picture deleted successfully"}
