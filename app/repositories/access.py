from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access import AccessRoleRule, BusinessElementModel, RoleModel


async def list_roles(db: AsyncSession) -> list[RoleModel]:
    result = await db.execute(select(RoleModel).order_by(RoleModel.code))
    return list(result.scalars().all())


async def get_role(db: AsyncSession, code: str) -> RoleModel | None:
    return await db.get(RoleModel, code)


async def list_business_elements(db: AsyncSession) -> list[BusinessElementModel]:
    result = await db.execute(select(BusinessElementModel).order_by(BusinessElementModel.code))
    return list(result.scalars().all())


async def get_business_element(db: AsyncSession, code: str) -> BusinessElementModel | None:
    return await db.get(BusinessElementModel, code)


async def list_access_rules(db: AsyncSession) -> list[AccessRoleRule]:
    result = await db.execute(
        select(AccessRoleRule).order_by(
            AccessRoleRule.role_code,
            AccessRoleRule.business_element_code,
        )
    )
    return list(result.scalars().all())


async def get_access_rule(db: AsyncSession, rule_id: int) -> AccessRoleRule | None:
    return await db.get(AccessRoleRule, rule_id)


async def get_access_rule_by_role_element(
    db: AsyncSession,
    role_code: str,
    business_element_code: str,
) -> AccessRoleRule | None:
    result = await db.execute(
        select(AccessRoleRule).where(
            AccessRoleRule.role_code == role_code,
            AccessRoleRule.business_element_code == business_element_code,
        )
    )
    return result.scalar_one_or_none()


async def list_access_rules_for_role(
    db: AsyncSession,
    role_code: str,
) -> list[AccessRoleRule]:
    result = await db.execute(
        select(AccessRoleRule).where(AccessRoleRule.role_code == role_code)
    )
    return list(result.scalars().all())
