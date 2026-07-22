from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse, UserLogin, LoginResponse
from app.database import get_db
from app.services import user as user_service

router = APIRouter()

@router.get("/health", status_code=200)
async def check_health():
    return {
        "status": "ok"
    }


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:

    return await user_service.register_user(db, user_create)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK
)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    return await user_service.login(db, user_login)