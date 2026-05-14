from backend.core import security, exceptions
from backend.core.config import settings
from backend.modules.users import models as usermodels
from backend.modules.auth import schemas, models as authmodels
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from fastapi import Request, Response
from jose import jwt, JWTError
from datetime import datetime, timezone


def register_user(
        user_data: schemas.RegisterRequest,
        db: Session
) -> usermodels.User:
    existing_user = db.execute(
        select(usermodels.User).where(
            usermodels.User.email == user_data.email
        )
    ).scalar_one_or_none()

    if existing_user:
        raise exceptions.UserEmailAlreadyExists()
    
    if user_data.password != user_data.password_repeat:
        raise exceptions.ValidationError('Password do not match')
    
    hashed_pwd = security.hash_password(user_data.password)

    db_user = usermodels.User(
        email = user_data.email,
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        password = hashed_pwd,
        birth_date = user_data.birth_date,
        is_active = True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def login_user(
        response: Response,
        email: str,
        password: str,
        db: Session
) -> schemas.TokenResponse:
    
    user = db.execute(
        select(usermodels.User).where(usermodels.User.email == email)
    ).scalar_one_or_none()

    if not user or not security.verify_password(plain_password=password, hashed_pwd=user.password):
        raise exceptions.InvalidCredentials()
    
    access_token = security.create_access_jwt(user=user)
    refresh_token = security.create_refresh_jwt(user=user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 60 * 60 * 24
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def refresh_tokens(
        request: Request,
        db: Session
) -> schemas.TokenResponse:
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise exceptions.CredentialsException()
    
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != settings.REFRESH_TOKEN_TYPE:
            raise JWTError
        
        jti = payload.get("jti")

        if not jti:
            raise JWTError
        
        blacklisted = db.execute(
            select(authmodels.TokenBlackList).where(
                authmodels.TokenBlackList.jti == jti
            )
        ).scalar_one_or_none()

        if blacklisted:
            raise JWTError
        
    except JWTError:
        db.rollback()
        raise exceptions.CredentialsException()
    
    user_id = payload.get("sub")

    if not user_id:
        raise exceptions.CredentialsException()
    
    user = db.execute(
        select(usermodels.User).where(
            usermodels.User.id == int(user_id)
        )
    ).scalar_one_or_none()



    if not user:
        raise exceptions.CredentialsException()
    
    new_access_token = security.create_access_jwt(user=user)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


def logout_user(
        request: Request,
        response: Response,
        access_token: str,
        db: Session
) -> schemas.LogoutResponse:
    try:
        #BLACKLIST ACCESS TOKEN
        access_payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        access_jti = access_payload.get("jti")
        access_exp = access_payload.get("exp")
        if not access_jti or not access_exp:
            raise JWTError
        access_expires_at = datetime.fromtimestamp(
            access_exp,
            tz=timezone.utc
        )

        db.add(
            authmodels.TokenBlackList(
                jti=access_jti,
                expires_at=access_expires_at
            )
        )

        #BLACKLIST REFRESH TOKEN
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            refresh_payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            refresh_jti = refresh_payload.get("jti")
            refresh_exp = refresh_payload.get("exp")

            if not refresh_jti or not refresh_exp:
                raise JWTError
            
            refresh_expires_at = datetime.fromtimestamp(
                refresh_exp,
                tz=timezone.utc
            )

            db.add(authmodels.TokenBlackList(
                jti=refresh_jti,
                expires_at=refresh_expires_at
            ))

    except JWTError:
        raise exceptions.CredentialsException()
    

    db.commit()
    
    response.delete_cookie("refresh_token")

    return {
        "detail": "Successfully logged out"
    }
    

def cleanup_token_blacklist(db: Session):
    db.query(authmodels.TokenBlackList).filter(
        authmodels.TokenBlackList.expires_at < datetime.now(timezone.utc)
    ).delete(synchronize_session=False)

    db.commit()