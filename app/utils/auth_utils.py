from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext

from app.config import SECRET_KEY, ALGORITHM
from app.database.models import UserBackend, ChatUserRequest, SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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
    if user and verify(password, user.password):
        return user
    return False

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

# CHECKED
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta if expires_delta else datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.now() + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
