from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models
from app.core.exceptions import AppError
from app.core.security import create_access_token
from app.database import get_db
from app.schemas import APIResponse, TokenResponse, UserRegisterRequest, UserResponse
from app.services.auth import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=APIResponse[UserResponse])
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    user = register_user(
        db,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    return APIResponse(
        data=UserResponse(id=user.id, email=user.email, full_name=user.full_name)
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise AppError(
            "Incorrect email or password.",
            status_code=401,
            code="invalid_credentials",
        )

    token = create_access_token(subject=user.email)
    return APIResponse(data=TokenResponse(access_token=token))
