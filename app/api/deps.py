from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.exceptions import AppError
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email = payload.get("sub")
        if not email:
            raise AppError("Invalid authentication token.", status_code=401, code="invalid_token")
    except JWTError:
        raise AppError("Invalid authentication token.", status_code=401, code="invalid_token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise AppError("User not found.", status_code=401, code="user_not_found")

    return user
