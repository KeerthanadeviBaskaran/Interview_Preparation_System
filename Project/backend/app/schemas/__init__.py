from app.schemas.user import UserBase, UserCreate, UserUpdate, UserLogin, UserResponse
from app.schemas.token import Token, TokenPayload
from app.schemas.student_profile import (
    StudentProfileBase,
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentProfileResponse,
)
from app.schemas.resume import ResumeUploadResponse
from app.schemas.role import RoleSelectRequest, RoleResponse, AvailableRolesResponse, PREDEFINED_ROLES
from app.schemas.resume_analysis import ResumeAnalysisResponse
from app.schemas.skill_gap import SkillGapResponse
from app.schemas.roadmap import SkillResource, RoadmapSkillItem, RoadmapResponse
from app.schemas.interview import QuestionGenerateRequest, InterviewQuestionResponse, InterviewSessionResponse

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenPayload",
    "StudentProfileBase",
    "StudentProfileCreate",
    "StudentProfileUpdate",
    "StudentProfileResponse",
    "ResumeUploadResponse",
    "RoleSelectRequest",
    "RoleResponse",
    "AvailableRolesResponse",
    "PREDEFINED_ROLES",
    "ResumeAnalysisResponse",
    "SkillGapResponse",
    "SkillResource",
    "RoadmapSkillItem",
    "RoadmapResponse",
    "QuestionGenerateRequest",
    "InterviewQuestionResponse",
    "InterviewSessionResponse",
]
