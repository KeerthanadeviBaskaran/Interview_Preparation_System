from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LearningProgressBase(BaseModel):
    """
    Base Pydantic schema for Learning Progress data validation.
    """
    skill_name: str = Field(..., min_length=1, max_length=255, description="Name of the skill being tracked")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Progress percentage from 0 to 100")


class LearningProgressCreate(LearningProgressBase):
    """
    Schema required for creating a new learning progress entry.
    """
    pass


class LearningProgressUpdate(BaseModel):
    """
    Schema for updating an existing learning progress entry.
    """
    skill_name: Optional[str] = Field(None, min_length=1, max_length=255)
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)


class LearningProgressResponse(LearningProgressBase):
    """
    Response schema returning complete learning progress data.
    """
    id: int
    user_id: int
    status: str = Field(..., description="Derived status: Needs Improvement, Improving, or Strong")
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)