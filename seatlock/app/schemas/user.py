from pydantic import BaseModel, EmailStr, ConfigDict


class BaseUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr  # automatic 422 error if emails fails
    mobile_no: str
    model_config = ConfigDict(from_attributes=True)
    # this enabales orm to be validated against a pydantic model


class CreateUser(BaseUser):
    password: str


class ReturnUser(BaseModel):
    pass
