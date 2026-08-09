from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.resume import ResumeUploadResponse
from app.services.resume_service import ResumeService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/resume", tags=["Resume Upload"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="PDF Resume File (max 5MB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a PDF resume file.
    Validates file type (PDF only), file size (<= 5MB), and PDF magic header.
    Stores file securely in uploads directory and links file path to user's profile.
    """
    return await ResumeService.upload_resume(db=db, user_id=current_user.id, file=file)


@router.get("/download")
def download_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download or stream the currently uploaded PDF resume file.
    """
    filename, filepath = ResumeService.get_resume_filepath(db=db, user_id=current_user.id)
    if not filename or not filepath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No uploaded resume found for this user."
        )
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/pdf"
    )


@router.delete("", status_code=status.HTTP_200_OK)
def delete_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete the uploaded resume file from disk and clear DB record.
    """
    success = ResumeService.delete_resume(db=db, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume file found to delete."
        )
    return {"message": "Resume file deleted successfully"}
