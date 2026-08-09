from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile
    from app.models.resume_analysis import ResumeAnalysis
    from app.models.skill_gap import SkillGapAnalysis
    from app.models.roadmap import Roadmap
    from app.models.interview import InterviewSession
    from app.models.feedback import Feedback


class User(Base):
    """
    SQLAlchemy ORM Model representing a registered User in SQLite database.
    Stores authentication details, active status, role, and timezone-aware timestamps.
    Maintains relationships with StudentProfile, ResumeAnalysis, SkillGapAnalysis, Roadmap, and InterviewSessions.
    """
    __tablename__ = "users"

    # Primary key auto-incrementing integer identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Unique email address used for login and user identification
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # Optional user full name
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Passlib bcrypt hashed password string
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Account status flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Audit creation and update timestamps (UTC timezone aware)
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

    # 1-to-1 ORM relationship to StudentProfile
    profile: Mapped[Optional["StudentProfile"]] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # 1-to-1 ORM relationship to ResumeAnalysis
    resume_analysis: Mapped[Optional["ResumeAnalysis"]] = relationship(
        "ResumeAnalysis",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # 1-to-1 ORM relationship to SkillGapAnalysis
    skill_gap_analysis: Mapped[Optional["SkillGapAnalysis"]] = relationship(
        "SkillGapAnalysis",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # 1-to-1 ORM relationship to Roadmap
    roadmap: Mapped[Optional["Roadmap"]] = relationship(
        "Roadmap",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # 1-to-Many ORM relationship to InterviewSessions
    interview_sessions: Mapped[List["InterviewSession"]] = relationship(
        "InterviewSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # 1-to-Many ORM relationship to Feedback
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        cascade="all, delete-orphan"
    )

    # 1-to-Many ORM relationship to LearningProgress
    learning_progress: Mapped[List["LearningProgress"]] = relationship(
        "LearningProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )
