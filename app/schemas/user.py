from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):

    first_name: str
    last_name: str
    middle_name: str | None = None
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    email: EmailStr | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
