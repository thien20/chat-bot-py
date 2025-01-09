from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from jose import JWTError, jwt
from datetime import timedelta

from app.models.schemas import Token
from app.utils import *
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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
