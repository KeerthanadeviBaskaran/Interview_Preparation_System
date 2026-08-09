import os
from typing import Optional, Dict, Any, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.student_profile import StudentProfile
from app.services.student_profile_service import StudentProfileService
from app.schemas.student_profile import StudentProfileCreate
from app.utils.file_handler import (
    validate_pdf_file,
    save_resume_file,
    delete_resume_file,
    UPLOAD_DIR,
)


class ResumeService:
    """
    Service logic for handling PDF resume uploads, storage, and database persistence.
    """

    @staticmethod
    async def upload_resume(db: Session, user_id: int, file: UploadFile) -> Dict[str, Any]:
        """
        Reads, validates, saves the PDF resume file, and updates the database record.
        """
        # Read file contents
        contents = await file.read()

        # Validate PDF extension, MIME type, size limit (5MB), and magic header
        validate_pdf_file(file=file, contents=contents)

        # Get or create user profile
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile:
            # Create a default profile if one does not exist yet
            profile = StudentProfileService.create(
                db=db,
                user_id=user_id,
                profile_in=StudentProfileCreate(
                    target_role="Software Engineer",
                    experience_level="Entry Level"
                )
            )

        # Remove existing resume file if previously uploaded
        if profile.resume_filename:
            delete_resume_file(profile.resume_filename)

        # Save new resume file to disk
        secure_filename, absolute_path = save_resume_file(user_id=user_id, file=file, contents=contents)

        # Update profile database record
        profile.resume_filename = secure_filename
        db.add(profile)
        db.commit()
        db.refresh(profile)

        return {
            "filename": secure_filename,
            "filepath": absolute_path,
            "size_bytes": len(contents),
            "content_type": file.content_type or "application/pdf",
            "message": "Resume uploaded successfully"
        }

    @staticmethod
    def get_resume_filepath(db: Session, user_id: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Retrieves the local disk path of the user's stored resume PDF.
        Returns (filename, absolute_filepath).
        """
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile or not profile.resume_filename:
            return None, None
        
        filepath = os.path.join(UPLOAD_DIR, profile.resume_filename)
        if not os.path.exists(filepath):
            return profile.resume_filename, None
            
        return profile.resume_filename, filepath

    @staticmethod
    def delete_resume(db: Session, user_id: int) -> bool:
        """
        Deletes the resume file from disk and clears the filename in DB.
        """
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile or not profile.resume_filename:
            return False

        # Remove file from disk
        delete_resume_file(profile.resume_filename)

        # Update DB record
        profile.resume_filename = None
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return True
