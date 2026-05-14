from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core import exceptions
from backend.core.security import hash_password
from backend.modules.users import models, schemas
from typing import List


def update_profile(
        current_user: models.User,
        user_update_data: schemas.UserUpdate,
        db: Session
) -> models.User:
    db_user = current_user

    if not db_user:
        raise exceptions.UserNotFound()
    
    update_data = user_update_data.model_dump(exclude_unset=True)
    password_repeat = update_data.pop("password_repeat", None)

    for key, value in update_data.items():
        if key == "password":
            if value:
                if password_repeat and value != password_repeat:
                    raise exceptions.ValidationError("Passwords do not match")

                setattr(db_user, "password", hash_password(value))
                continue

        if key == "email":
            existing = db.execute(
                select(models.User).where(models.User.email == value)
            ).scalar_one_or_none()

            if existing and existing.id != db_user.id:
                raise exceptions.UserEmailAlreadyExists()
            
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(
        user_delete_data: schemas.UserDelete,
        current_user: models.User,
        db: Session
) -> models.User:
    db_user = current_user

    if not db_user:
        raise exceptions.UserNotFound()
    
    delete_data = user_delete_data.model_dump(exclude_unset=True)
    for key, value in delete_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_my_profile(
        current_user: models.User,
        db: Session
) -> models.User:
    return current_user


def get_profile(
        user_id: int,
        current_user: models.User,
        db: Session
) -> models.User:
    user = db.execute(
        select(models.User).where(
            models.User.id == user_id,
            models.User.is_active == True
        )
    ).scalar_one_or_none()

    if not user:
        raise exceptions.UserNotFound()
    
    return user


def get_all_profiles(
        current_user: models.User,
        db: Session
) -> List[models.User]:
    users = db.execute(
        select(models.User).where(models.User.is_active == True)
    ).scalars().all()

    return users


def get_profiles_by_first_name(
        first_name: str,
        current_user: models.User,
        db: Session
) -> List[models.User]:
    users = db.execute(
        select(models.User).where(
            models.User.first_name == first_name,
            models.User.is_active == True
        )
    ).scalars().all()

    return users