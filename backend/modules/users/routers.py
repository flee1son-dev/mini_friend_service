from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from backend.core import exceptions
from backend.core.security import get_current_user
from backend.core.database import get_db
from backend.modules.users import schemas, models, services
from typing import List

router = APIRouter(prefix="/users", tags=["User"])


#Get all users
@router.get("", response_model=List[schemas.UserResponse], status_code=status.HTTP_200_OK)
def all_profiles(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_all_profiles(current_user=current_user, db=db)


#My profile
@router.get("/me", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
def me(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_my_profile(current_user=current_user, db=db)


#Get users by first name
@router.get("/search", response_model=List[schemas.UserResponse], status_code=status.HTTP_200_OK)
def profiles_by_first_name(
    first_name: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_profiles_by_first_name(
        first_name=first_name,
        current_user=current_user,
        db=db
    )


#Get user's profile
@router.get("/{user_id}", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
def get_profile(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.get_profile(
        user_id=user_id,
        current_user=current_user,
        db=db
    )


#Update my profile
@router.put("/me/update", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
def update_profile(
    update_data: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return services.update_profile(
        current_user=current_user,
        user_update_data=update_data,
        db=db
    )


#Delete my profile
@router.delete("/me/delete", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
def delete_profile(
        delete_data: schemas.UserDelete,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return services.delete_user(
        user_delete_data=delete_data,
        current_user=current_user,
        db=db
    )