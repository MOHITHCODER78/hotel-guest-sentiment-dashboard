from sqlalchemy.orm import Session

from app import models
from app.core.exceptions import AppError
from app.core.security import hash_password, verify_password


def register_user(db: Session, email: str, password: str, full_name: str | None = None) -> models.User:
    normalized_email = email.strip().lower()
    existing = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing:
        raise AppError("Email is already registered.", status_code=409, code="email_exists")

    user = models.User(
        email=normalized_email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    normalized_email = email.strip().lower()
    user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
