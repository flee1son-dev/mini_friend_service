from pydantic import BaseModel, Field, model_validator
from enum import Enum as PyEnum
from typing import Optional
from backend.modules.friendships.models import FriendshipStatus
from backend.modules.users.schemas import UserResponse
from backend.core.exceptions import ValidationError


class FriendshipBase(BaseModel):
    requester_id: int = Field(..., description="Requester's primary key")
    addressee_id: int = Field(..., description="Addressee's primary key")
    status: FriendshipStatus = Field(default=FriendshipStatus.pending, description="friend request status")

    @model_validator(mode="before")
    def check_requester_addressee(cls, values: dict) -> dict:
        if values.get("requester_id") == values.get("addressee_id"):
            raise ValueError("Requester and addressee can't be same user")
        return values


class FriendshipCreate(FriendshipBase):
    pass


class FriendshipResponse(FriendshipBase):
    id: int = Field(..., description="Friendship's primary key")
    requester: Optional[UserResponse] = None
    addressee: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class FriendshipUpdate(BaseModel):
    status: Optional[FriendshipStatus] = Field(default=None, description="Friendship status")

    @model_validator(mode="before")
    def validate_status(cls, values:dict) -> dict:
        status = values.get("status")
        if status is not None:
            try:
                if isinstance(status, str):
                    values["status"] = FriendshipStatus(status)
                elif not isinstance(status, FriendshipStatus):
                    raise ValueError("Status must be a valid FriendshipStatus")
            except ValueError:
                raise ValidationError(f"Invalid status: {status}")
        return values

