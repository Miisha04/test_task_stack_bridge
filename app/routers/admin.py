from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.policy import AccessContext, BusinessElement, Permission, require_permissions
from app.schemas.access import (
    AccessRuleCreate,
    AccessRuleResponse,
    AccessRuleUpdate,
    BusinessElementCreate,
    BusinessElementResponse,
    BusinessElementUpdate,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserRoleUpdate,
)
from app.schemas.user import UserResponse
from app.services import access as access_service


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/roles", 
    status_code=status.HTTP_200_OK,
    response_model=list[RoleResponse],
)
async def list_roles(
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.READ_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> list[RoleResponse]:
    return await access_service.list_roles(db)


@router.post(
    "/roles", 
    response_model=RoleResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_role(
    role_create: RoleCreate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.CREATE})
    ),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    return await access_service.create_role(db, role_create)


@router.patch(
    "/roles/{role_code}", 
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK
)
async def update_role(
    role_code: str,
    role_update: RoleUpdate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.UPDATE_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    return await access_service.update_role(db, role_code, role_update)


@router.delete(
    "/roles/{role_code}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_role(
    role_code: str,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.DELETE_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> None:
    return await access_service.delete_role(db, role_code)


@router.get(
    "/business-elements", 
    response_model=list[BusinessElementResponse],
    status_code=status.HTTP_200_OK
)
async def list_business_elements(
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.READ_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> list[BusinessElementResponse]:
    return await access_service.list_business_elements(db)


@router.post(
    "/business-elements",
    response_model=BusinessElementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_business_element(
    business_element_create: BusinessElementCreate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.CREATE})
    ),
    db: AsyncSession = Depends(get_db),
) -> BusinessElementResponse:
    return await access_service.create_business_element(db, business_element_create)


@router.patch(
    "/business-elements/{business_element_code}", 
    response_model=BusinessElementResponse
)
async def update_business_element(
    business_element_code: str,
    business_element_update: BusinessElementUpdate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.UPDATE_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> BusinessElementResponse:
    return await access_service.update_business_element(
        db,
        business_element_code,
        business_element_update,
    )


@router.delete(
    "/business-elements/{business_element_code}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_business_element(
    business_element_code: str,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.DELETE_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> None:
    return await access_service.delete_business_element(db, business_element_code)


@router.get(
    "/access-rules", 
    response_model=list[AccessRuleResponse],
    status_code=status.HTTP_200_OK
)
async def list_access_rules(
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.READ_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> list[AccessRuleResponse]:
    return await access_service.list_access_rules(db)


@router.post(
    "/access-rules",
    response_model=AccessRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_access_rule(
    access_rule_create: AccessRuleCreate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.CREATE})
    ),
    db: AsyncSession = Depends(get_db),
) -> AccessRuleResponse:
    return await access_service.create_access_rule(db, access_rule_create)


@router.patch(
    "/access-rules/{rule_id}", 
    response_model=AccessRuleResponse,
    status_code=status.HTTP_200_OK
)
async def update_access_rule(
    rule_id: int,
    access_rule_update: AccessRuleUpdate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.UPDATE_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> AccessRuleResponse:
    return await access_service.update_access_rule(db, rule_id, access_rule_update)


@router.delete(
    "/access-rules/{rule_id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_access_rule(
    rule_id: int,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.ACCESS_RULES, {Permission.DELETE_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> None:
    return await access_service.delete_access_rule(db, rule_id)


@router.get(
    "/users", 
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
async def list_users(
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.USERS, {Permission.READ_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    return await access_service.list_users(db)


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
async def update_user_role(
    user_id: int,
    user_role_update: UserRoleUpdate,
    access_context: AccessContext = Depends(
        require_permissions(BusinessElement.USERS, {Permission.UPDATE_ALL})
    ),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await access_service.update_user_role(
        db,
        user_id,
        user_role_update.role,
    )
