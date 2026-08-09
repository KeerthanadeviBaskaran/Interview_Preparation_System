from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import decode_token
from app.core.exceptions import CredentialsException, InactiveUserException
from app.services.user_service import UserService
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/oauth")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise CredentialsException(detail="Could not validate credentials or token expired")
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise CredentialsException(detail="Invalid token payload")
        
    user = UserService.get_by_id(db, user_id=int(user_id))
    if not user:
        raise CredentialsException(detail="User not found")
        
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user
