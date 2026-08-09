from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.student_profile import StudentProfile
from app.services.student_profile_service import StudentProfileService
from app.schemas.student_profile import StudentProfileCreate
from app.schemas.role import PREDEFINED_ROLES, RoleSelectRequest, RoleResponse, AvailableRolesResponse


class RoleService:
    """
    Business logic for target role selection and persistence.
    """

    @staticmethod
    def get_available_roles() -> AvailableRolesResponse:
        """
        Returns list of standard predefined interview roles.
        """
        return AvailableRolesResponse(roles=PREDEFINED_ROLES)

    @staticmethod
    def get_user_role(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves user's currently selected target role and experience level.
        """
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        if not profile:
            return None
        return {
            "user_id": user_id,
            "target_role": profile.target_role,
            "experience_level": profile.experience_level,
        }

    @staticmethod
    def select_or_update_role(db: Session, user_id: int, role_in: RoleSelectRequest) -> RoleResponse:
        """
        Sets or updates user's target role in the database.
        Creates a new Student Profile record if one does not exist yet.
        """
        profile = StudentProfileService.get_by_user_id(db, user_id=user_id)
        
        if not profile:
            # Create profile record with selected target role
            profile = StudentProfileService.create(
                db=db,
                user_id=user_id,
                profile_in=StudentProfileCreate(
                    target_role=role_in.target_role.strip(),
                    experience_level=role_in.experience_level.strip() if role_in.experience_level else "Entry Level"
                )
            )
        else:
            # Update existing profile record
            profile.target_role = role_in.target_role.strip()
            if role_in.experience_level:
                profile.experience_level = role_in.experience_level.strip()
            db.add(profile)
            db.commit()
            db.refresh(profile)

        return RoleResponse(
            user_id=user_id,
            target_role=profile.target_role,
            experience_level=profile.experience_level,
            message="Target role updated successfully"
        )
