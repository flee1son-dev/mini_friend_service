from fastapi import APIRouter, Depends, Response, Request, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth import services, schemas as authschemas
from modules.users import schemas as userschemas
from core.security import oauth2scheme


router = APIRouter(prefix="/auth", tags=["Auth"])


#register user
@router.post("/register", response_model=userschemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: authschemas.RegisterRequest,
    db: Session = Depends(get_db)
):
    return services.register_user(user_data=user_data, db=db)


#login user
@router.post("/login", response_model=authschemas.TokenResponse, status_code=status.HTTP_200_OK)
def login(
    response: Response,
    form_data:  OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return services.login_user(
        response=response,
        email=form_data.username,
        password=form_data.password,
        db=db
    )


#refresh user's access token
@router.post("/refresh", response_model=authschemas.TokenResponse, status_code=status.HTTP_200_OK)
def refresh(
        request: Request,
        db: Session = Depends(get_db)
):
    return services.refresh_tokens(
        request=request,
        db=db
    )


#logout user
@router.post("/logout", response_model=authschemas.LogoutResponse, status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    response: Response,
    token: str = Depends(oauth2scheme),
    db: Session = Depends(get_db)
):
    BackgroundTasks().add_task(services.cleanup_token_blacklist, db)
    return services.logout_user(
        request=request,
        response=response,
        access_token=token,
        db=db
    )
