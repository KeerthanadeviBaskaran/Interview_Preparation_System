from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.learning_progress import (
    LearningProgressCreate,
    LearningProgressUpdate,
    LearningProgressResponse,
)
from app.services.learning_progress_service import LearningProgressService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["Learning Progress"])


@router.get("", response_model=list[LearningProgressResponse])
def get_learning_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all learning progress entries for the authenticated user.
    """
    progress_list = LearningProgressService.get_by_user_id(db, user_id=current_user.id)
    return progress_list


@router.post("", response_model=LearningProgressResponse, status_code=status.HTTP_201_CREATED)
def create_learning_progress(
    progress_in: LearningProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new learning progress entry for a skill.
    """
    return LearningProgressService.create(db=db, user_id=current_user.id, progress_in=progress_in)


@router.put("/{progress_id}", response_model=LearningProgressResponse)
def update_learning_progress(
    progress_id: int,
    progress_in: LearningProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing learning progress entry.
    """
    progress = LearningProgressService.get_by_id(db, progress_id=progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning progress entry not found"
        )
    
    # Verify ownership
    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this progress entry"
        )
    
    return LearningProgressService.update(db=db, db_progress=progress, progress_in=progress_in)


@router.delete("/{progress_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a learning progress entry.
    """
    progress = LearningProgressService.get_by_id(db, progress_id=progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning progress entry not found"
        )
    
    # Verify ownership
    if progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this progress entry"
        )
    
    LearningProgressService.delete(db=db, db_progress=progress)
    return None
