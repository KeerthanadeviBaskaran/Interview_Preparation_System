from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.role import RoleSelectRequest, RoleResponse, AvailableRolesResponse
from app.services.role_service import RoleService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/role", tags=["Role Selection"])


@router.get("/available", response_model=AvailableRolesResponse)
def get_available_roles():
    """
    Retrieve list of curated target job roles available for interview preparation.
    """
    return RoleService.get_available_roles()


@router.get("/me", response_model=RoleResponse)
def get_my_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve the currently selected target role of the authenticated user.
    """
    role_info = RoleService.get_user_role(db=db, user_id=current_user.id)
    if not role_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target role not selected yet. Please select a role first."
        )
    return RoleResponse(
        user_id=role_info["user_id"],
        target_role=role_info["target_role"],
        experience_level=role_info["experience_level"],
        message="Current target role retrieved"
    )


@router.post("/me", response_model=RoleResponse, status_code=status.HTTP_200_OK)
def select_role(
    role_in: RoleSelectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Select target job role for interview preparation.
    Stores selection in the database.
    """
    return RoleService.select_or_update_role(db=db, user_id=current_user.id, role_in=role_in)


@router.put("/me", response_model=RoleResponse)
def update_role(
    role_in: RoleSelectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update selected target job role and experience level.
    """
    return RoleService.select_or_update_role(db=db, user_id=current_user.id, role_in=role_in)
