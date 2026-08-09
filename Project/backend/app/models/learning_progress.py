from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

if TYPE_CHECKING:
    from app.models.user import User


class LearningProgress(Base):
    """
    SQLAlchemy ORM Model storing learning progress for skills identified by skill-gap/roadmap system.
    Establishes relationship with User entity.
    """
    __tablename__ = "learning_progress"

    # Primary key identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key relationship with User model
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # Skill being tracked
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Progress percentage (0-100)
    progress_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Status derived from progress_percentage:
    # 0-39 = Needs Improvement
    # 40-69 = Improving
    # 70-100 = Strong
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Needs Improvement")

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="learning_progress")