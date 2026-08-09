from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class ResumeAnalysis(Base):
    """
    SQLAlchemy ORM Model storing structured resume analysis extracted from PDF documents.
    Establishes a 1-to-1 relationship with the User entity.
    """
    __tablename__ = "resume_analyses"

    # Primary key identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # 1-to-1 Foreign key relationship with User model
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    # Raw extracted PDF text
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Extracted categorization fields stored as JSON in SQLite
    programming_languages: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    frameworks: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    databases: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    technical_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    projects: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    certifications: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    experience: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    education: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Overview summary
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit timestamps
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

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="resume_analysis")
