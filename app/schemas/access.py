from pydantic import BaseModel, ConfigDict


class RoleResponse(BaseModel):
    code: str
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    code: str
    name: str
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class BusinessElementResponse(BaseModel):
    code: str
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BusinessElementCreate(BaseModel):
    code: str
    name: str
    description: str | None = None


class BusinessElementUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class UserRoleUpdate(BaseModel):
    role: str


class AccessRuleBase(BaseModel):
    role_code: str
    business_element_code: str
    read_permission: bool = False
    read_all_permission: bool = False
    create_permission: bool = False
    update_permission: bool = False
    update_all_permission: bool = False
    delete_permission: bool = False
    delete_all_permission: bool = False


class AccessRuleCreate(AccessRuleBase):
    pass


class AccessRuleUpdate(BaseModel):
    read_permission: bool | None = None
    read_all_permission: bool | None = None
    create_permission: bool | None = None
    update_permission: bool | None = None
    update_all_permission: bool | None = None
    delete_permission: bool | None = None
    delete_all_permission: bool | None = None


class AccessRuleResponse(AccessRuleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
