from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.learning_progress import LearningProgress
from app.schemas.learning_progress import LearningProgressCreate, LearningProgressUpdate


class LearningProgressService:
    """
    Service logic for learning progress tracking operations.
    """

    @staticmethod
    def _derive_status(progress_percentage: float) -> str:
        """
        Derives status from progress percentage.
        0-39 = Needs Improvement
        40-69 = Improving
        70-100 = Strong
        """
        if progress_percentage >= 70:
            return "Strong"
        elif progress_percentage >= 40:
            return "Improving"
        else:
            return "Needs Improvement"

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> List[LearningProgress]:
        """
        Fetch all progress entries for a specific user.
        """
        return db.query(LearningProgress).filter(LearningProgress.user_id == user_id).all()

    @staticmethod
    def get_by_id(db: Session, progress_id: int) -> Optional[LearningProgress]:
        """
        Fetch progress entry by primary key ID.
        """
        return db.query(LearningProgress).filter(LearningProgress.id == progress_id).first()

    @staticmethod
    def create(db: Session, user_id: int, progress_in: LearningProgressCreate) -> LearningProgress:
        """
        Create a new learning progress entry.
        """
        status = LearningProgressService._derive_status(progress_in.progress_percentage)
        
        db_progress = LearningProgress(
            user_id=user_id,
            skill_name=progress_in.skill_name,
            progress_percentage=progress_in.progress_percentage,
            status=status
        )
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return db_progress

    @staticmethod
    def update(db: Session, db_progress: LearningProgress, progress_in: LearningProgressUpdate) -> LearningProgress:
        """
        Update an existing learning progress entry.
        """
        update_data = progress_in.model_dump(exclude_unset=True)
        
        # Update progress percentage if provided
        if "progress_percentage" in update_data:
            update_data["status"] = LearningProgressService._derive_status(update_data["progress_percentage"])
        
        for field, value in update_data.items():
            setattr(db_progress, field, value)

        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return db_progress

    @staticmethod
    def delete(db: Session, db_progress: LearningProgress) -> bool:
        """
        Delete a learning progress entry.
        """
        db.delete(db_progress)
        db.commit()
        return True