from pydantic import BaseModel, Field


class ReadinessResponse(BaseModel):
    """
    Response schema for interview readiness score.
    """
    readiness_score: float = Field(..., ge=0.0, le=100.0, description="Overall readiness score from 0 to 100")
    performance_level: str = Field(..., description="Derived performance level: Needs Improvement, Developing, Good, or Interview Ready")
    breakdown: dict = Field(default_factory=dict, description="Component breakdown of the score")