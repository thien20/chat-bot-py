from fastapi import Depends, HTTPException, status, APIRouter, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from datetime import timedelta

from typing import Annotated
from app.models.schemas import Token
from app.utils.auth_utils import *
from ..database.models import SessionLocal
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response,
                                form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                db: Session = Depends(get_db)):
    """
    - DECS: This function is to for user `LOGIN` and get the access token
    - PROBLEM - SOLVED: 
    - When you declare other function parameters that are not part of the path parameters, 
    they are automatically interpreted as "query" parameters.
    - STATUS: DONE

    NOTE: We should not return the refresh token here. 
        - HTTP-only Cookies (recommended): Store the refresh token in a Secure, SameSite, and HTTP-only cookie to mitigate XSS attacks. 
        Use the Secure flag if your application uses HTTPS. 
        - Avoid storing refresh tokens in localStorage or sessionStorage.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token = create_access_token(
                                    data={"sub": user.username}, 
                                    expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                                    )
    
    refresh_token = create_refresh_token(data={"sub": user.username})
    # Set refresh token in a secure HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict",
    ) # put to the http-only cookie

    # This is the return i did saw in real life mobile app --> i still consider it as a questionable practice
    return {"access_token": access_token,
            "refresh_token": refresh_token, 
            "token_type": "bearer"} 

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str, 
    db: Session = Depends(get_db)
):
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
        
        # Ensure the user still exists
        user = get_user_credentials(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User no longer exists"
            )
        
        # Generate a new access token
        access_token = create_access_token(
            data={"sub": username}, 
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Optionally, issue a new refresh token
        new_refresh_token = create_refresh_token(data={"sub": username})
        
        return {
            "access_token": access_token, 
            "refresh_token": new_refresh_token, 
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid refresh token"
        )