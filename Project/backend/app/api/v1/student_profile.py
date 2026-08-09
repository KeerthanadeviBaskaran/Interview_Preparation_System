from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.student_profile import (
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentProfileResponse,
)
from app.services.student_profile_service import StudentProfileService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["Student Profile"])


@router.get("/me", response_model=StudentProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve the Student Profile of the currently logged-in user.
    """
    profile = StudentProfileService.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the current user. Please create one."
        )
    return profile


@router.post("/me", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_in: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new Student Profile for the currently logged-in user.
    Throws HTTP 400 if a profile already exists for this user.
    """
    existing_profile = StudentProfileService.get_by_user_id(db, user_id=current_user.id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists for this user. Use PUT to update instead."
        )
    return StudentProfileService.create(db=db, user_id=current_user.id, profile_in=profile_in)


@router.put("/me", response_model=StudentProfileResponse)
def update_my_profile(
    profile_in: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the Student Profile for the currently logged-in user.
    """
    profile = StudentProfileService.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please create a profile first."
        )
    return StudentProfileService.update(db=db, db_profile=profile, profile_in=profile_in)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete the Student Profile for the currently logged-in user.
    """
    profile = StudentProfileService.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found."
        )
    StudentProfileService.delete(db=db, db_profile=profile)
    return None
