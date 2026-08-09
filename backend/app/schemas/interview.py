from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class QuestionGenerateRequest(BaseModel):
    """
    Request payload for customizing AI interview question generation.
    """
    num_questions: Optional[int] = Field(5, ge=1, le=20, description="Total number of interview questions to generate")
    difficulty: Optional[str] = Field(None, description="Preferred overall difficulty: Easy, Medium, or Hard")


class InterviewQuestionResponse(BaseModel):
    """
    Pydantic schema for individual generated interview question including candidate response.
    """
    id: int
    session_id: int
    question: str = Field(..., serialization_alias="question", validation_alias="question_text")
    category: str = Field(..., description="Category: Technical, Coding, Behavioral, Scenario-Based, HR")
    difficulty: str = Field(..., description="Difficulty: Easy, Medium, Hard")
    expected_topics: List[str] = Field(default_factory=list)
    ideal_answer_points: List[str] = Field(default_factory=list)
    evaluation_criteria: List[str] = Field(default_factory=list)
    estimated_time_minutes: int = 5
    user_answer: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class InterviewSessionResponse(BaseModel):
    """
    Pydantic schema for an interview session containing all generated questions and progress.
    """
    id: int
    user_id: int
    target_role: str
    experience_level: str
    total_questions: int
    answered_questions_count: int = 0
    status: str = Field("generated", description="Session status: generated, in_progress, completed")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None
    questions: List[InterviewQuestionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
