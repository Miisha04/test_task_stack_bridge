from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserResponse, UserCreate
from app.security import hash_password
from app.repositories import user as user_repos


async def register_user(
    db: AsyncSession,
    user_create: UserCreate
) -> UserResponse:

    new_user = User(
        **user_create.model_dump(exclude={"password"}),
        hashed_password=user_create.password
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

    


    