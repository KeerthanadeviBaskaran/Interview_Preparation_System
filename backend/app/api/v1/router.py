from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.student_profile import router as profile_router
from app.api.v1.resume import router as resume_router
from app.api.v1.role import router as role_router
from app.api.v1.resume_analysis import router as resume_analysis_router
from app.api.v1.skill_gap import router as skill_gap_router
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.interviews import router as interview_router
from app.api.v1.learning_progress import router as learning_progress_router
from app.api.v1.readiness import router as readiness_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(profile_router)
api_router.include_router(resume_router)
api_router.include_router(role_router)
api_router.include_router(resume_analysis_router)
api_router.include_router(skill_gap_router)
api_router.include_router(roadmap_router)
api_router.include_router(interview_router)
api_router.include_router(learning_progress_router)
api_router.include_router(readiness_router)
