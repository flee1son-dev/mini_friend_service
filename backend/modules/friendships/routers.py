from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.core import exceptions
from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.modules.friendships import schemas, services
from backend.modules.users import models as UserModels
from typing import List

router = APIRouter(prefix="/friendships", tags=["Friendships"])


@router.post("/", response_model=schemas.FriendshipResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_data: schemas.FriendshipCreate,
    current_user: UserModels.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.create_friend_request(
        current_user=current_user,
        addressee_id=request_data.addressee_id,
        db=db
    )


@router.patch("/{friendship_id}/accept", response_model=schemas.FriendshipResponse, status_code=status.HTTP_200_OK)
def accept_request(
    friendship_id: int,
    current_user: UserModels.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.accept_friend_request(
        friendship_id=friendship_id,
        current_user=current_user,
        db=db
    )


@router.patch("/{friendship_id}/reject", response_model=schemas.FriendshipResponse, status_code=status.HTTP_200_OK)
def reject_request(
    friendship_id: int,
    current_user: UserModels.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.reject_friend_request(
        friendship_id=friendship_id,
        current_user=current_user,
        db=db
    )


@router.delete("/{friendship_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_friendship(
    friendship_id: int,
    current_user: UserModels.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    services.remove_friendship(
        friendship_id=friendship_id,
        current_user=current_user,
        db=db
    )


@router.get("/requests", response_model=List[schemas.FriendshipResponse], status_code=status.HTTP_200_OK)
def get_requests(
    current_user: UserModels.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_friend_requests(
        current_user=current_user,
        db=db
    )


@router.get("/friends", response_model=List[schemas.UserResponse], status_code=status.HTTP_200_OK)
def get_friends(
    current_user: UserModels.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_friends(
        current_user=current_user,
        db=db
    )

