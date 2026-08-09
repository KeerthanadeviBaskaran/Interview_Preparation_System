from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FeedbackResponse(BaseModel):
    """
    Pydantic schema for returning detailed feedback for a single interview question answer.
    """
    id: int
    user_id: int
    session_id: int
    question_id: int
    score: float = Field(..., ge=0.0, le=100.0, description="Overall score from 0-100")
    relevance_score: float = Field(..., ge=0.0, le=100.0, description="Relevance to the question")
    technical_correctness: float = Field(..., ge=0.0, le=100.0, description="Technical accuracy")
    completeness: float = Field(..., ge=0.0, le=100.0, description="Completeness of the answer")
    clarity: float = Field(..., ge=0.0, le=100.0, description="Clarity and communication")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths in the answer")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses or gaps")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    ideal_answer: Optional[str] = Field(None, description="Ideal answer for comparison")
    evaluation: Optional[str] = Field(None, description="Overall evaluation summary")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmitRequest(BaseModel):
    """
    Pydantic schema for submitting an answer to an interview question.
    """
    user_answer: str = Field(..., min_length=1, max_length=5000, description="Candidate's answer text")


class AnswerSubmitResponse(BaseModel):
    """
    Pydantic schema for response after submitting an answer.
    """
    question_id: int
    session_id: int
    user_answer: str
    answered_at: datetime
    feedback: Optional[FeedbackResponse] = None
    message: str = "Answer submitted successfully"


class InterviewCompletionResponse(BaseModel):
    """
    Pydantic schema for response after completing an interview session.
    """
    session_id: int
    user_id: int
    target_role: str
    experience_level: str
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall interview score")
    total_questions: int
    answered_questions: int
    completed_at: datetime
    duration_seconds: Optional[int] = None
    overall_strengths: List[str] = Field(default_factory=list)
    overall_weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    feedback_summary: List[FeedbackResponse] = Field(default_factory=list)
    message: str = "Interview completed successfully"


class InterviewEvaluationSummary(BaseModel):
    """
    Pydantic schema for summary evaluation metrics across the entire interview.
    """
    session_id: int
    average_score: float
    category_scores: dict = Field(default_factory=dict, description="Average scores per question category")
    total_time_minutes: Optional[int] = None
    performance_trend: str = Field(..., description="Performance trend: improving, stable, or declining")
