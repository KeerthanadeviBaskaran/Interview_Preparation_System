from typing import Optional
from sqlalchemy.orm import Session
from app.models.student_profile import StudentProfile
from app.schemas.student_profile import StudentProfileCreate, StudentProfileUpdate


class StudentProfileService:
    """
    Business logic and database service layer for Student Profile operations.
    """

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[StudentProfile]:
        """
        Fetch profile by associated user ID.
        """
        return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()

    @staticmethod
    def get_by_id(db: Session, profile_id: int) -> Optional[StudentProfile]:
        """
        Fetch profile by primary key profile ID.
        """
        return db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()

    @staticmethod
    def create(db: Session, user_id: int, profile_in: StudentProfileCreate) -> StudentProfile:
        """
        Create a new Student Profile linked to the given user_id.
        """
        db_profile = StudentProfile(
            user_id=user_id,
            phone_number=profile_in.phone_number,
            bio=profile_in.bio,
            target_role=profile_in.target_role,
            experience_level=profile_in.experience_level,
            target_companies=profile_in.target_companies or [],
            skills=profile_in.skills or [],
            education=profile_in.education,
            graduation_year=profile_in.graduation_year,
            github_url=profile_in.github_url,
            linkedin_url=profile_in.linkedin_url,
            portfolio_url=profile_in.portfolio_url,
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def update(db: Session, db_profile: StudentProfile, profile_in: StudentProfileUpdate) -> StudentProfile:
        """
        Update an existing Student Profile with new attributes.
        """
        update_data = profile_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)

        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def delete(db: Session, db_profile: StudentProfile) -> bool:
        """
        Delete a Student Profile from the database.
        """
        db.delete(db_profile)
        db.commit()
        return True
