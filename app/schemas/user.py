from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):

    first_name: str
    last_name: str
    middle_name: str | None
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
