from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserLogin, LoginResponse
from app.security import hash_password, create_access_token, verify_password
from app.repositories import user as user_repos


async def register_user(
    db: AsyncSession,
    user_create: UserCreate
) -> UserResponse:

    new_user = User(
        **user_create.model_dump(exclude={"password"}),
        hashed_password=hash_password(user_create.password)
    )

    db.add(new_user)

    try:
        await db.commit()
    except Exception:
        await db.rollback()

    user = await user_repos.get_user(db, user_create.email)
    if not user:
        raise Exception("Error during user registration")

    return UserResponse.model_validate(user)


async def login(
    db: AsyncSession,
    user_login: UserLogin
) -> LoginResponse:
    
    user = await user_repos.get_user(db, user_login.email)
    if not user:
        raise Exception("There is no such user")

    is_verified = verify_password(user_login.password, user.hashed_password)
    if not is_verified:
        raise Exception("Not auntificated")

    return LoginResponse(
        access_token=create_access_token(user_login.model_dump())
    )