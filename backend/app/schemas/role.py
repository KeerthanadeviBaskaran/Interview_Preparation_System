from typing import List, Optional
from pydantic import BaseModel, Field


# List of standard, curated target roles for interview preparation
PREDEFINED_ROLES = [
    "Backend Engineer",
    "Frontend Engineer",
    "Fullstack Developer",
    "AI / ML Engineer",
    "DevOps Engineer",
    "Data Scientist",
    "Mobile App Developer (iOS/Android)",
    "Cloud Architect",
    "Cybersecurity Engineer",
    "Product Manager",
    "QA Automation Engineer",
    "Systems Software Engineer"
]


class RoleSelectRequest(BaseModel):
    """
    Pydantic schema for selecting or updating target job role.
    """
    target_role: str = Field(..., min_length=2, max_length=100, description="Target job role (e.g. Backend Engineer)")
    experience_level: Optional[str] = Field("Entry Level", max_length=50, description="Target experience level")


class RoleResponse(BaseModel):
    """
    Pydantic schema returning user's currently selected target role.
    """
    user_id: int
    target_role: str
    experience_level: str
    message: str = "Role updated successfully"


class AvailableRolesResponse(BaseModel):
    """
    Pydantic schema returning all pre-configured target roles.
    """
    roles: List[str]
