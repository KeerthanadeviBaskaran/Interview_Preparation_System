from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SkillResource(BaseModel):
    """
    Recommended learning resource link.
    """
    title: str
    url: str


class RoadmapSkillItem(BaseModel):
    """
    Detailed roadmap item for a missing or recommended skill.
    """
    skill_name: str
    phase: str = Field(..., description="Roadmap phase: immediate, short_term, medium_term, or long_term")
    learning_objective: str
    difficulty: str = Field("Intermediate", description="Difficulty level: Beginner, Intermediate, or Advanced")
    estimated_duration: str
    resources: List[SkillResource] = Field(default_factory=list)
    practice_project: str
    interview_tips: str


class RoadmapResponse(BaseModel):
    """
    Pydantic schema for returning complete Personalized Learning Roadmap response.
    """
    id: int
    user_id: int
    target_role: str
    experience_level: str
    total_skills_to_learn: int
    immediate_phase: List[RoadmapSkillItem] = Field(default_factory=list, description="Immediate (1–2 Weeks)")
    short_term_phase: List[RoadmapSkillItem] = Field(default_factory=list, description="Short-Term (1 Month)")
    medium_term_phase: List[RoadmapSkillItem] = Field(default_factory=list, description="Medium-Term (2–3 Months)")
    long_term_phase: List[RoadmapSkillItem] = Field(default_factory=list, description="Long-Term (Beyond 3 Months)")
    summary_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
