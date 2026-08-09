from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class StudentProfile(Base):
    """
    SQLAlchemy ORM Model representing a Student Profile in the system.
    Establishes a 1-to-1 relationship with the User model.
    Stores professional preferences, target job roles, skills, and social links.
    """
    __tablename__ = "student_profiles"

    # Primary key identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # 1-to-1 Foreign key relationship with User entity
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    # Personal and background information
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Career targets & experience level
    target_role: Mapped[str] = mapped_column(String(100), nullable=False, default="Software Engineer")
    experience_level: Mapped[str] = mapped_column(String(50), nullable=False, default="Entry Level")
    
    # Complex data stored as JSON arrays in SQLite
    target_companies: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    skills: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)

    # Education history
    education: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Professional URLs
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Saved resume reference
    resume_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

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

    # ORM relationship back to User entity
    user: Mapped["User"] = relationship("User", back_populates="profile")
