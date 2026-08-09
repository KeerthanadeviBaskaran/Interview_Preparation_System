from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

if TYPE_CHECKING:
    from app.models.user import User


class InterviewSession(Base):
    """
    SQLAlchemy ORM Model representing an Interview Preparation Session.
    Stores generated question set metadata, target role, difficulty, timing tracking, and completion status.
    """
    __tablename__ = "interview_sessions"

    # Primary key identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key relationship to User model
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    target_role: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_level: Mapped[str] = mapped_column(String(50), nullable=False, default="Entry Level")
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    answered_questions_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="generated")  # generated, in_progress, completed

    # Timing & Duration tracking attributes
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="interview_sessions")
    questions: Mapped[List["InterviewQuestion"]] = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.id"
    )


class InterviewQuestion(Base):
    """
    SQLAlchemy ORM Model representing an individual generated interview question.
    Stores question content, category, difficulty level, expected topics, ideal answer points,
    evaluation criteria, estimated time, candidate submitted answers, and submission timestamp.
    """
    __tablename__ = "interview_questions"

    # Primary key identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key relationship to InterviewSession model
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # Technical, Coding, Behavioral, Scenario-Based, HR
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)  # Easy, Medium, Hard

    # Detailed guide attributes stored as JSON arrays in SQLite
    expected_topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    ideal_answer_points: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    evaluation_criteria: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    estimated_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    # Candidate response text & submission timestamp
    user_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship back to InterviewSession
    session: Mapped["InterviewSession"] = relationship("InterviewSession", back_populates="questions")
