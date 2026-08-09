from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class ResumeAnalysisResponse(BaseModel):
    """
    Pydantic Schema for structured Resume Analysis response.
    """
    id: int
    user_id: int
    programming_languages: List[str]
    frameworks: List[str]
    databases: List[str]
    technical_skills: List[str]
    projects: List[Dict[str, Any]]
    certifications: List[str]
    experience: Dict[str, Any]
    education: Dict[str, Any]
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
