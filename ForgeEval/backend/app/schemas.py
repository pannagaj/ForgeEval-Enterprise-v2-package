from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class SubmitIn(BaseModel):
    language: Literal["python", "javascript", "java"]
    source_code: str = Field(min_length=1, max_length=50000)

class ChallengeOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    difficulty: str
    tags: list
    starter_code: dict
    model_config = {"from_attributes": True}
