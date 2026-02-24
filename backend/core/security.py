from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from jose import JWTError
from backend.core.config import settings
from backend.core import exceptions
from backend.core.database import get_db
from backend.modules.users import models, schemas
from backend.modules.auth.models import TokenBlackList
import jwt
import uuid

"""PASSWORDS"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_password, hashed_pwd)

"""JWT TOKENS"""
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE = settings.ACCESS_TOKEN_EXPIRES_MINUTES
REFRESH_TOKEN_EXPIRE = settings.REFRESH_TOKEN_EXPIRES_DAYS
ACCESS_TOKEN_TYPE = settings.ACCESS_TOKEN_TYPE_FIELD
REFRESH_TOKEN_TYPE = settings.REFRESH_TOKEN_TYPE_FIELD
TOKEN_TYPE_FIELD = "type"

oauth2scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#UTILS
def encode_jwt(
        payload: dict,
        private_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        expire_minutes: int = ACCESS_TOKEN_EXPIRE,
        expire_days: timedelta | None = None
) -> str:
    to_encode = payload.copy()

    now = datetime.now(timezone.utc)
    if expire_days:
        expire = now + expire_days
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
            exp=expire,
            iat=now
    )

    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm
    )

    return encoded


def create_jwt(
        type: str,
        payload: dict,
        expire_minutes: int = ACCESS_TOKEN_EXPIRE,
        expire_days: timedelta | None = None
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: type
    }
    
    jwt_payload.update(payload)

    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_days=expire_days
    )

#GENERAL
def create_access_jwt(user: models.User) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "name": user.first_name,
        "email": user.email,
        "jti": str(uuid.uuid4())
    }

    return create_jwt(
        type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=ACCESS_TOKEN_EXPIRE,
        expire_days=None
    )


def create_refresh_jwt(user: models.User):
    jwt_payload = {
        "sub": str(user.id),
        "name": user.first_name,
        "email": user.email,
        "jti": str(uuid.uuid4())
    }

    return create_jwt(
        type=REFRESH_TOKEN_TYPE,
        payload=jwt_payload,
        expire_days=timedelta(days=REFRESH_TOKEN_EXPIRE)
    )


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2scheme)
):
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get(TOKEN_TYPE_FIELD)

        if token_type != ACCESS_TOKEN_TYPE:
            raise JWTError
    except JWTError:
        raise exceptions.CredentialsException()
    
    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or not jti:
        raise exceptions.CredentialsException()
    
    blacklisted = db.execute(select(TokenBlackList).where(TokenBlackList.jti == jti)).scalar_one_or_none()

    if blacklisted:
        raise exceptions.CredentialsException()
    
    user = db.execute(
        select(models.User).where(models.User.id == int(user_id))
    ).scalar_one_or_none()
    

    if not user:
        raise exceptions.CredentialsException()
    
    return user