from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.readiness import ReadinessResponse
from app.services.readiness_service import ReadinessService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/readiness", tags=["Interview Readiness"])


@router.get("", response_model=ReadinessResponse)
def get_readiness_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate and return the interview readiness score for the authenticated user.
    
    The score is calculated from existing data:
    - Interview performance: 40%
    - Learning progress: 30%
    - Skill gap: 20%
    - Roadmap completion: 10%
    
    Returns overall score (0-100) and performance level.
    """
    return ReadinessService.calculate_readiness_score(db=db, user_id=current_user.id)