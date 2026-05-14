from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_
from backend.modules.friendships import models as FriendshipModels
from backend.modules.users import models as UserModels
from backend.core import exceptions
from typing import List


#UTILS
def get_friendship(
        friendship_id: int,
        db: Session
) -> FriendshipModels.Friendship:
    friendship = db.execute(
        select(FriendshipModels.Friendship).where(
            FriendshipModels.Friendship.id == friendship_id
        )
    ).scalar_one_or_none()

    if not friendship:
        raise exceptions.FriendShipNotFound()

    return friendship


#GENERAL
def create_friend_request(
        current_user: UserModels.User,
        addressee_id: int,
        db: Session
) -> FriendshipModels.Friendship:
    requester_id = current_user.id

    existing =  db.execute(
            select(FriendshipModels.Friendship).where(
                or_(
                    and_(
                        FriendshipModels.Friendship.requester_id == requester_id,
                        FriendshipModels.Friendship.addressee_id == addressee_id
                    ),
                    and_(
                        FriendshipModels.Friendship.requester_id == addressee_id,
                        FriendshipModels.Friendship.addressee_id == requester_id
                    )
                )
            )
        ).scalar_one_or_none()

    if existing:
        raise exceptions.FriendRequestAlreadyExists()
    
    status = FriendshipModels.FriendshipStatus.pending
    friendship = FriendshipModels.Friendship(
        requester_id = requester_id,
        addressee_id = addressee_id,
        status = status
    )

    db.add(friendship)
    db.commit()
    db.refresh(friendship)

    return friendship


def accept_friend_request(
        friendship_id: int,
        current_user: UserModels.User,
        db: Session
) -> FriendshipModels.Friendship:
    friendship = get_friendship(friendship_id=friendship_id, db=db)
    if current_user.id != friendship.addressee_id:
        raise exceptions.PermissionDeniedException(
            detail="You are not allowed to accept this friendship request"
        )
     
    if friendship.status == FriendshipModels.FriendshipStatus.accepted:
        raise exceptions.FriendRequestAlreadyAccepted()
    
    if friendship.status != FriendshipModels.FriendshipStatus.pending:
        raise exceptions.FriendRequestAlreadyRejected()
    
    friendship.status = FriendshipModels.FriendshipStatus.accepted

    db.commit()
    db.refresh(friendship)
    
    
    return friendship


def reject_friend_request(
        friendship_id: int,
        current_user: UserModels.User,
        db: Session
) -> FriendshipModels.Friendship:
    friendship = get_friendship(friendship_id=friendship_id, db=db)
    if current_user.id != friendship.addressee_id:
        raise exceptions.PermissionDeniedException(
            detail="You are not allowed to reject this friendship request"
        )
    
    if friendship.status == FriendshipModels.FriendshipStatus.rejected:
        raise exceptions.FriendRequestAlreadyRejected()
    
    if friendship.status != FriendshipModels.FriendshipStatus.pending:
        raise exceptions.FriendRequestAlreadyAccepted()
    
    friendship.status = FriendshipModels.FriendshipStatus.rejected

    db.commit()
    db.refresh(friendship)
    
    
    return friendship


def remove_friendship(
        friendship_id: int,
        current_user: UserModels.User,
        db: Session
) -> None:
    friendship = get_friendship(friendship_id=friendship_id, db=db)
    if current_user.id != friendship.requester_id and current_user.id != friendship.addressee_id:
        raise exceptions.PermissionDeniedException(
            detail="You are not allowed to remove this friendship request"
        )

    
    db.delete(friendship)
    db.commit()
    
    

def get_friend_requests(
        current_user: UserModels.User,
        db: Session
) -> List[FriendshipModels.Friendship]:
    friend_requests_list = db.execute(
        select(FriendshipModels.Friendship).where(
            FriendshipModels.Friendship.addressee_id == current_user.id,
            FriendshipModels.Friendship.status == FriendshipModels.FriendshipStatus.pending
        )
    ).scalars().all()

    return friend_requests_list

def get_friends(
        current_user: UserModels.User,
        db: Session
) -> List[UserModels.User]:
    friendships= db.execute(
        select(FriendshipModels.Friendship).where(
            or_(
                FriendshipModels.Friendship.addressee_id == current_user.id,
                FriendshipModels.Friendship.requester_id == current_user.id
            ),
            FriendshipModels.Friendship.status == FriendshipModels.FriendshipStatus.accepted
        )
    ).scalars().all()

    friends = []
    
    for friendship in friendships:
        if friendship.requester_id == current_user.id:
            friends.append(friendship.addressee)
        else:
            friends.append(friendship.requester)

    return friends
    

