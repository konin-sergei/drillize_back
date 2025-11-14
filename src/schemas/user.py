from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str


class UserOutSchema(BaseModel):
    error: str| None
    id: int
    email: str | None
    confirm_email: bool

    class Config:
        from_attributes = True

class UserProfileSchema(BaseModel):
    id: int
    email: str | None


class EmailConfirmSchema(BaseModel):
    email: EmailStr
    code: str
