from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.skill_gap import SkillGapResponse
from app.services.skill_gap_service import SkillGapService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap Analysis"])


@router.post("/analyze", response_model=SkillGapResponse, status_code=status.HTTP_200_OK)
def analyze_skill_gap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Compares candidate's extracted resume skills with the predefined requirements for their selected target role.
    Generates Strong Skills, Missing Skills, Recommended Skills to Learn, Skill Match Percentage (0-100),
    and Overall Assessment, and stores the result in SQLite database.
    """
    return SkillGapService.analyze_skill_gap(db=db, user_id=current_user.id)


@router.get("/result", response_model=SkillGapResponse)
def get_skill_gap_result(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve stored Skill Gap Analysis result for the authenticated user.
    """
    result = SkillGapService.get_user_skill_gap(db=db, user_id=current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill gap analysis not found. Please trigger analysis using POST /api/v1/skill-gap/analyze."
        )
    return result
