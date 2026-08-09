from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.roadmap import RoadmapResponse
from app.services.roadmap_service import RoadmapService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmap"])


@router.post("/generate", response_model=RoadmapResponse, status_code=status.HTTP_200_OK)
def generate_roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generates a personalized, multi-horizon learning roadmap divided into:
    1. Immediate (1–2 Weeks)
    2. Short-Term (1 Month)
    3. Medium-Term (2–3 Months)
    4. Long-Term (Beyond 3 Months)

    For each missing skill, provides learning objective, difficulty, estimated duration,
    recommended learning resources (title + URL), practice project suggestion, and interview preparation tips.
    Persists the generated roadmap in SQLite database.
    """
    return RoadmapService.generate_roadmap(db=db, user_id=current_user.id)


@router.get("", response_model=RoadmapResponse)
def get_roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve existing stored Personalized Learning Roadmap for the authenticated user.
    """
    roadmap = RoadmapService.get_user_roadmap(db=db, user_id=current_user.id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found. Please generate your roadmap using POST /api/v1/roadmap/generate."
        )
    return roadmap
