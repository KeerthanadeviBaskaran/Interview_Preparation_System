from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.resume_analysis import ResumeAnalysisResponse
from app.services.resume_analysis_service import ResumeAnalysisService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/resume", tags=["Resume Analysis"])


@router.post("/analyze", response_model=ResumeAnalysisResponse, status_code=status.HTTP_200_OK)
def analyze_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Extract text from uploaded PDF resume, analyze technical skills, programming languages,
    frameworks, databases, projects, certifications, education, and experience,
    and save the extracted information to the SQLite database.
    """
    return ResumeAnalysisService.analyze_user_resume(db=db, user_id=current_user.id)


@router.get("/analysis", response_model=ResumeAnalysisResponse)
def get_resume_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve existing stored resume analysis for the authenticated user.
    """
    analysis = ResumeAnalysisService.get_user_analysis(db=db, user_id=current_user.id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found. Please trigger analysis first using POST /resume/analyze."
        )
    return analysis
