from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access import AccessRoleRule, BusinessElementModel, RoleModel
from app.models.user import User
from app.repositories import access as access_repo
from app.repositories import user as user_repo
from app.schemas.access import (
    AccessRuleCreate,
    AccessRuleUpdate,
    AccessRuleResponse,
    BusinessElementCreate,
    BusinessElementUpdate,
    BusinessElementResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse
)
from app.schemas.user import UserResponse


CORE_BUSINESS_ELEMENTS = {"tickets", "users", "access_rules"}


async def list_roles(db: AsyncSession) -> list[RoleResponse]:
    roles_obj = await access_repo.list_roles(db)
    roles = [
        RoleResponse.model_validate(obj)
        for obj in roles_obj
    ]
    return roles


async def create_role(
    db: AsyncSession,
    role_create: RoleCreate,
) -> RoleModel:
    existing_role = await access_repo.get_role(db, role_create.code)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    role = RoleModel(**role_create.model_dump())
    db.add(role)
    try:
        await db.commit()
        await db.refresh(role)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during role creation",
        )

    return role


async def update_role(
    db: AsyncSession,
    role_code: str,
    role_update: RoleUpdate,
) -> RoleModel:
    role = await access_repo.get_role(db, role_code)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    for field, value in role_update.model_dump(exclude_unset=True).items():
        setattr(role, field, value)

    try:
        await db.commit()
        await db.refresh(role)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during role update",
        )

    return role


async def delete_role(
    db: AsyncSession,
    role_code: str,
) -> None:
    role = await access_repo.get_role(db, role_code)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if role_code == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin role cannot be deleted",
        )

    await db.delete(role)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during role deletion",
        )


async def list_business_elements(db: AsyncSession) -> list[BusinessElementResponse]:
    elements_obj = await access_repo.list_business_elements(db)
    elements = [
        BusinessElementResponse.model_validate(obj)
        for obj in elements_obj
    ]
    return elements 


async def create_business_element(
    db: AsyncSession,
    business_element_create: BusinessElementCreate,
) -> BusinessElementModel:
    existing_business_element = await access_repo.get_business_element(
        db,
        business_element_create.code,
    )
    if existing_business_element:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business element already exists",
        )

    business_element = BusinessElementModel(**business_element_create.model_dump())
    db.add(business_element)
    try:
        await db.commit()
        await db.refresh(business_element)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during business element creation",
        )

    return business_element


async def update_business_element(
    db: AsyncSession,
    business_element_code: str,
    business_element_update: BusinessElementUpdate,
) -> BusinessElementModel:
    business_element = await access_repo.get_business_element(db, business_element_code)
    if not business_element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found",
        )

    for field, value in business_element_update.model_dump(exclude_unset=True).items():
        setattr(business_element, field, value)

    try:
        await db.commit()
        await db.refresh(business_element)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during business element update",
        )

    return business_element


async def delete_business_element(
    db: AsyncSession,
    business_element_code: str,
) -> None:
    if business_element_code in CORE_BUSINESS_ELEMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Core business element cannot be deleted",
        )

    business_element = await access_repo.get_business_element(db, business_element_code)
    if not business_element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found",
        )

    await db.delete(business_element)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during business element deletion",
        )


async def list_access_rules(db: AsyncSession) -> list[AccessRuleResponse]:
    access_rules_obj = await access_repo.list_access_rules(db)
    access_rules = [
        AccessRuleResponse.model_validate(obj)
        for obj in access_rules_obj
    ]
    return access_rules



async def create_access_rule(
    db: AsyncSession,
    access_rule_create: AccessRuleCreate,
) -> AccessRoleRule:
    role = await access_repo.get_role(db, access_rule_create.role_code)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    business_element = await access_repo.get_business_element(
        db,
        access_rule_create.business_element_code,
    )
    if not business_element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business element not found",
        )

    existing_rule = await access_repo.get_access_rule_by_role_element(
        db,
        access_rule_create.role_code,
        access_rule_create.business_element_code,
    )
    if existing_rule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Access rule already exists",
        )

    access_rule = AccessRoleRule(**access_rule_create.model_dump())
    db.add(access_rule)

    try:
        await db.commit()
        await db.refresh(access_rule)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during access rule creation",
        )

    return access_rule


async def update_access_rule(
    db: AsyncSession,
    rule_id: int,
    access_rule_update: AccessRuleUpdate,
) -> AccessRoleRule:
    access_rule = await access_repo.get_access_rule(db, rule_id)
    if not access_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access rule not found",
        )

    update_data = access_rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(access_rule, field, value)

    if (
        access_rule.role_code == "admin"
        and access_rule.business_element_code == "access_rules"
        and not (
            access_rule.read_all_permission
            and access_rule.create_permission
            and access_rule.update_all_permission
            and access_rule.delete_all_permission
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin access_rules permissions cannot be disabled",
        )

    try:
        await db.commit()
        await db.refresh(access_rule)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during access rule update",
        )

    return access_rule


async def delete_access_rule(
    db: AsyncSession,
    rule_id: int,
) -> None:
    access_rule = await access_repo.get_access_rule(db, rule_id)
    if not access_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access rule not found",
        )

    if access_rule.role_code == "admin" and access_rule.business_element_code == "access_rules":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin access_rules rule cannot be deleted",
        )

    await db.delete(access_rule)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during access rule deletion",
        )


async def list_users(db: AsyncSession) -> list[UserResponse]:
    users_obj = await user_repo.list_users(db)
    users = [
        UserResponse.model_validate(obj)
        for obj in users_obj
    ]
    return users


async def update_user_role(
    db: AsyncSession,
    user_id: int,
    role_code: str,
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    role = await access_repo.get_role(db, role_code)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    user.role = role_code
    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error during user role update",
        )

    return user
