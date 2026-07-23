import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, RefreshToken
from app.schemas.user import UserResponse, UserCreate, UserLogin, LoginResponse
from app.security import hash_password, create_access_token, verify_password, create_refresh_token, hash_refresh
from app.repositories import user as user_repos
from app.settings import get_settings


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


def _build_access_payload(email: str, now: datetime) -> dict:
    settings = get_settings()

    return {
        "sub": email,
        "token_type": "access",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience_user,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_access_token_expire_minutes)).timestamp()),
    }


def _build_refresh_payload(email: str, jti: uuid.UUID, now: datetime) -> tuple[dict, datetime]:

    settings = get_settings()
    expires_at = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    return {
        "sub": email,
        "jti": str(jti),
        "token_type": "refresh",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience_refresh,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp())
    }, expires_at


async def login(
    db: AsyncSession,
    user_login: UserLogin,
    user_agent: str | None = None,
    ip: str | None = None,
) -> LoginResponse:
    
    user = await user_repos.get_user(db, user_login.email)
    if not user:
        raise Exception("There is no such user")

    is_verified = verify_password(user_login.password, user.hashed_password)
    if not is_verified:
        raise Exception("Not auntificated")

    now = datetime.now()    
    access_payload = _build_access_payload(user_login.email, now)

    refresh_jti = uuid.uuid4()
    refresh_payload, refresh_expires_at = _build_refresh_payload(user_login.email, refresh_jti, now)
    refresh_token = create_refresh_token(refresh_payload)

    refresh_obj = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh(refresh_token),
        jti=refresh_jti,
        expires_at=refresh_expires_at,
        created_at=now,
        revoked_at=None,
        user_agent=user_agent,
        ip=ip,
    )

    db.add(refresh_obj)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
                                           
    return LoginResponse(
        access_token=create_access_token(access_payload),
        refresh_token=refresh_token
    )