from fastapi import APIRouter, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse, UserLogin, LoginResponse, UserUpdate
from app.database import get_db
from app.services import user as user_service
from app.policy import AccessContext, BusinessElement, Permission, require_permissions
from app.models.user import User

router = APIRouter(prefix="/user")


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:

    return await user_service.register_user(db, user_create)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse
)
async def login(
    user_login: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    return await user_service.login(
        db, 
        user_login, 
        request.headers.get("user-agent"),
        ip=request.client.host if request.client else None
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    return await user_service.logout(db, refresh_token)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse
)
async def get_current_user(
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.USERS, {Permission.READ})
    ),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await db.get(User, access_context.user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse
)
async def update_current_user(
    user_update: UserUpdate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.USERS, {Permission.UPDATE})
    ),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await user_service.update_user_profile(
        db,
        access_context.user_id,
        user_update,
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.USERS, {Permission.DELETE})
    ),
    db: AsyncSession = Depends(get_db)
) -> None:
    return await user_service.delete_user(db, access_context.user_id)
