from typing import Optional
from pydantic import BaseModel, EmailStr, constr


class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=4)


from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    agree_terms: bool = False
    agree_privacy: bool = False
    agree_marketing: bool = False



class PostCreateRequest(BaseModel):
    text: constr(min_length=4)


class PostUpdateRequest(BaseModel):
    text: constr(min_length=4)
