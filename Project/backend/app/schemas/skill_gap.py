from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class SkillGapResponse(BaseModel):
    """
    Pydantic schema for returning Skill Gap Analysis result.
    """
    id: int
    user_id: int
    target_role: str
    match_percentage: float = Field(..., ge=0.0, le=100.0, description="Overall skill alignment percentage")
    strong_skills: List[str] = Field(default_factory=list, description="Matched skills present in candidate resume")
    missing_skills: List[str] = Field(default_factory=list, description="Required role skills missing from resume")
    recommended_skills: List[str] = Field(default_factory=list, description="Prioritized skills recommended for learning")
    overall_assessment: str = Field(..., description="Qualitative evaluation summary")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
