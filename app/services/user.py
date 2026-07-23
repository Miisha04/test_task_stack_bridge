import uuid
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, RefreshToken
from app.schemas.user import UserResponse, UserCreate, UserLogin, LoginResponse, UserUpdate
from app.security import hash_password, create_access_token, verify_password, create_refresh_token, hash_refresh
from app.repositories import user as user_repos
from app.settings import get_settings


async def register_user(
    db: AsyncSession,
    user_create: UserCreate
) -> UserResponse:

    new_user = User(
        **user_create.model_dump(exclude={"password"}),
        hashed_password=hash_password(user_create.password),
        is_active=True,
        role="user",
    )

    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during user registration",
        ) from exc

    return UserResponse.model_validate(new_user)


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    is_verified = verify_password(user_login.password, user.hashed_password)
    if not is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    now = datetime.now(timezone.utc)
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
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        ) from exc
                                           
    return LoginResponse(
        access_token=create_access_token(access_payload),
        refresh_token=refresh_token
    )


async def logout(
    db: AsyncSession,
    refresh_token: str
) -> None:

    settings = get_settings()
    now = datetime.now(timezone.utc)

    try:
        payload = jwt.decode(
            refresh_token,
            settings.jwt_refresh_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience_refresh,
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    username = payload.get("sub")
    jti_raw = payload.get("jti")
    if not username or not jti_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    try:
        token_jti = uuid.UUID(str(jti_raw))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    refresh_obj = await user_repos.get_refresh_by_hash(db, hash_refresh(refresh_token))
    if not refresh_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_obj.jti != token_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_obj.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_obj.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = await user_repos.get_user(db, username)
    if not user or user.id != refresh_obj.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    refresh_obj.revoked_at = now
    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        ) from exc


async def update_user_profile(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate,
) -> UserResponse:
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        await db.commit()
        await db.refresh(user)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during user update",
        ) from exc

    return UserResponse.model_validate(user)


async def delete_user(
    db: AsyncSession,
    user_id: int
) -> None:
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_active = False
    now = datetime.now(timezone.utc)

    await user_repos.revoke_refresh(db, user_id, now)

    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during user deletion",
        ) from exc
