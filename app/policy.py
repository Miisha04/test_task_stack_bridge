from dataclasses import dataclass
from enum import Enum
from jose import JWTError, jwt
from fastapi import Request, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.settings import get_settings
from app.repositories.user import get_user
from app.repositories import access as access_repo
from app.database import get_db


class BusinessElement(str, Enum):
    TICKETS = "tickets"
    USERS = "users"
    ACCESS_RULES = "access_rules"


class Permission(str, Enum):
    READ = "read"
    READ_ALL = "read_all"
    CREATE = "create"
    UPDATE = "update"
    UPDATE_ALL = "update_all"
    DELETE = "delete"
    DELETE_ALL = "delete_all"

PERMISSION_FIELDS: dict[str, Permission] = {
    "read_permission": Permission.READ,
    "read_all_permission": Permission.READ_ALL,
    "create_permission": Permission.CREATE,
    "update_permission": Permission.UPDATE,
    "update_all_permission": Permission.UPDATE_ALL,
    "delete_permission": Permission.DELETE,
    "delete_all_permission": Permission.DELETE_ALL,
}

@dataclass(frozen=True)
class AccessContext:
    role: str
    permissions: dict[str, set[Permission]]
    user_id: int


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def _forbidden() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden",
    )


async def _get_user_from_jwt(
    request: Request,
    db: AsyncSession
) -> User:

    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise _unauthorized()

    token = auth.split(" ", 1)[1]
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience_user,
        )
        email = payload.get("sub")
        if not email or payload.get("token_type") != "access":
            raise _unauthorized()
    except JWTError:
        raise _unauthorized()
    
    user: User = await get_user(db, email)
    if not user or not user.is_active:
        raise _unauthorized()

    return user
    

async def get_access_context(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> AccessContext:

    user = await _get_user_from_jwt(request, db)
    rules = await access_repo.list_access_rules_for_role(db, user.role)
    permissions: dict[str, set[Permission]] = {}

    for rule in rules:
        permissions[rule.business_element_code] = {
            permission
            for field_name, permission in PERMISSION_FIELDS.items()
            if getattr(rule, field_name)
        }

    return AccessContext(
        role=user.role,
        permissions=permissions,
        user_id=user.id,
    )


def require_permissions(
    business_element: BusinessElement | str,
    required_permissions: set[Permission],
):
    if not required_permissions:
        raise ValueError("required_permissions cannot be empty")

    business_element_code = (
        business_element.value
        if isinstance(business_element, BusinessElement)
        else business_element
    )

    async def dependency(
        access_context: AccessContext = Depends(get_access_context),
    ) -> AccessContext:
        available_permissions = access_context.permissions.get(business_element_code, set())

        if not required_permissions.issubset(available_permissions):
            raise _forbidden()

        return access_context

    return dependency
