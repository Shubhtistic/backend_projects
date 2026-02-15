from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    name: str
    email: EmailStr


class CreateUser(BaseUser):
    password: str


class ReadUser(BaseUser):
    pass


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
