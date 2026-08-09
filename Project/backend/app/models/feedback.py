from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.interview import InterviewSession, InterviewQuestion


class Feedback(Base):
    """
    SQLAlchemy ORM Model storing feedback and evaluation for interview question answers.
    Establishes relationships with User, InterviewSession, and InterviewQuestion.
    Stores evaluation metrics, scores, strengths, weaknesses, and improvement suggestions.
    """
    __tablename__ = "feedback"

    # Primary key identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key relationships
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    # Evaluation metrics
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    technical_correctness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    completeness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    clarity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Detailed feedback stored as JSON arrays in SQLite
    strengths: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    weaknesses: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    suggestions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Text fields
    ideal_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="feedbacks")
    session: Mapped["InterviewSession"] = relationship("InterviewSession")
    question: Mapped["InterviewQuestion"] = relationship("InterviewQuestion")
