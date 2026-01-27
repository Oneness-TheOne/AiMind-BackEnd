from typing import Optional
from pydantic import BaseModel, EmailStr, constr


class LoginRequest(BaseModel):
    userid: constr(min_length=4, pattern=r"^[a-zA-Z0-9]+$")
    password: constr(min_length=4)


class SignupRequest(LoginRequest):
    name: constr(min_length=1)
    email: EmailStr
    url: Optional[str] = None


class PostCreateRequest(BaseModel):
    text: constr(min_length=4)


class PostUpdateRequest(BaseModel):
    text: constr(min_length=4)
