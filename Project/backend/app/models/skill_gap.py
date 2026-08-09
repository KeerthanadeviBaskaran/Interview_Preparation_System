from datetime import datetime, timezone
from typing import List
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class SkillGapAnalysis(Base):
    """
    SQLAlchemy ORM Model storing Skill Gap Analysis results.
    Compares candidate resume skills against target role requirements.
    Establishes a 1-to-1 relationship with User entity.
    """
    __tablename__ = "skill_gap_analyses"

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

    # Target role being analyzed
    target_role: Mapped[str] = mapped_column(String(100), nullable=False)

    # Score & Assessment
    match_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overall_assessment: Mapped[str] = mapped_column(Text, nullable=False)

    # Breakdown stored as JSON arrays in SQLite
    strong_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    recommended_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

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

    # Relationship back to User model
    user: Mapped["User"] = relationship("User", back_populates="skill_gap_analysis")
