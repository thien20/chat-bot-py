from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from jose import JWTError, jwt
from datetime import datetime, timedelta

from typing import Annotated
from app.models.schemas import Token
from app.database.models import UserBackend
from app.utils import *
from app import utils
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
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    """
    CHECK THE USER CREDENTIALS
    PROBLEM - SOLVED: 
    - When you declare other function parameters that are not part of the path parameters, 
    they are automatically interpreted as "query" parameters.
    - STATUS: DONE
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# CHECKED
def get_user_credentials(db: Session, username: str):
    """
    Desc: Get user from database using ORM instead of raw SQL - Backend to check the username from client
    Return: the user object from backend
    """
    statement = select(UserBackend).filter(UserBackend.username == username).limit(1)
    user = db.execute(statement).scalar()
    return user

# CHECKED
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_credentials(db, username)
    print(user.password)
    if user and utils.verify(password, user.password):
        return user
    return False

# CHECKED
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta if expires_delta else datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    """
    Desc: Handle the current user after `login` and `auth/token`
    Return: the user object from backend
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        user = get_user_credentials(db, username)
        return {"username": user.username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
