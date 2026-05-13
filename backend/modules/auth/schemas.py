from pydantic import BaseModel, Field, EmailStr
from modules.users.schemas import UserCreate


class TokenResponse(BaseModel):
    access_token: str = Field(..., description=("Access JWT token"))
    token_type: str = Field(default="bearer")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email")
    password: str = Field(..., description="User's password")

class RegisterRequest(UserCreate):
    pass


#logout
class LogoutResponse(BaseModel):
    detail: str = Field(default="Successfully logged out")
