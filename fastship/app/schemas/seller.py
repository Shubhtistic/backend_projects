from pydantic import BaseModel, EmailStr


class RegisterSeller(BaseModel):
    name: str
    email: EmailStr
    model_config = {"from_attributes": True}
