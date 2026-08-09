from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    """
    return AuthService.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user via JSON body and return JWT access and refresh tokens.
    """
    return AuthService.login_user(db=db, credentials=credentials)


@router.post("/login/oauth", response_model=Token)
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login form, required for Swagger UI interactive Auth.
    """
    credentials = UserLogin(email=form_data.username, password=form_data.password)
    return AuthService.login_user(db=db, credentials=credentials)


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Generate new access and refresh tokens using a valid refresh token.
    """
    return AuthService.refresh_access_token(db=db, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get profile information of currently authenticated user.
    """
    return current_user
