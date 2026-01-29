from typing import Optional, List
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


class CommunityPostCreateRequest(BaseModel):
    category_slug: constr(min_length=2)
    title: constr(min_length=5, max_length=200)
    content: constr(min_length=10)
    tags: List[str] = []
    images: List[str] = []


class CommunityPostUpdateRequest(BaseModel):
    category_slug: Optional[constr(min_length=2)] = None
    title: Optional[constr(min_length=5, max_length=200)] = None
    content: Optional[constr(min_length=10)] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None


class CommunityCommentCreateRequest(BaseModel):
    content: constr(min_length=1)
    parent_id: Optional[int] = None
