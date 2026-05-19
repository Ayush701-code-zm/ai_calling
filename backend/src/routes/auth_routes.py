from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user
from src.schemas.auth_schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.services.auth.service import auth_service

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(request: UserRegisterRequest):
    result = await auth_service.register_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    return TokenResponse(access_token=result["access_token"])


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    result = await auth_service.login_user(
        email=request.email,
        password=request.password,
    )
    return TokenResponse(access_token=result["access_token"])


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
    )
