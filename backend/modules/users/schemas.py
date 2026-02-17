from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date

#General fields
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email")
    first_name: str = Field(min_length=2, max_length=30, description="User's name")
    last_name: str = Field(min_length=2, max_length=50, description="User's last name")
    birth_date: Optional[date] = Field(description="User's birth date")

#Register
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=32, description="User's password")
    password_repeat: str = Field(..., min_length=8, max_length=32, description="User's repeat password")

#Response
class UserResponse(UserBase):
    id: int = Field(..., description="User's primary key")
    is_active: bool = Field(...)

    class Config:
        from_attributes=True

#Update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    first_name: Optional[str] = Field(default=None, min_length=2, max_length=30)
    last_name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    birth_date: Optional[date] = Field(default=None)

    password: Optional[str] = Field(default=None, min_length=8, max_length=32)
    password_repeat: Optional[str] = Field(default=None, min_length=8, max_length=32)

#Delete
class UserDelete(BaseModel):
    is_active: bool = Field(default=False, description="Set to false to deactivate user")