from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UserAlreadyExistsException, InvalidCredentialsException, CredentialsException


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate):
        existing_user = UserService.get_by_email(db, email=user_in.email)
        if existing_user:
            raise UserAlreadyExistsException()
        user = UserService.create(db, user_in=user_in)
        return user

    @staticmethod
    def login_user(db: Session, credentials: UserLogin) -> Token:
        user = UserService.authenticate(db, email=credentials.email, password=credentials.password)
        if not user:
            raise InvalidCredentialsException()
        if not user.is_active:
            raise CredentialsException(detail="Inactive user account")
            
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Token:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise CredentialsException(detail="Invalid or expired refresh token")
            
        user_id = payload.get("sub")
        if not user_id:
            raise CredentialsException(detail="Invalid token payload")
            
        user = UserService.get_by_id(db, user_id=int(user_id))
        if not user or not user.is_active:
            raise CredentialsException(detail="User not found or inactive")
            
        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)
        return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")
