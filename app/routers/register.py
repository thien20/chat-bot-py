from fastapi import Depends, Response, status, HTTPException, APIRouter

from app.schemas import User, ChatRequest, UserRegisterRequest
from app.database.models import UserBackend, ChatUserRequest, SessionLocal
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from fastapi.responses import HTMLResponse, JSONResponse

from typing import Annotated

from random import randint
import logging


router = APIRouter(
    prefix="",
    tags=["post"],
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# SHARE DATABASE SESSION
db_dependency = Annotated[Session, Depends(get_db)]



@router.post("/register", response_model=User)
async def register(new_user: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Desc: Handle logic register at Backend username
    Problem: Done the create user, but still got 500 for internal server error
    Status: Pending
    """
    
    new_user = create_user(db, new_user)
    statement = select(UserBackend).filter(UserBackend.username == new_user.username).limit(1)
    db_user_username = db.execute(statement).scalar().username
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    
    return new_user, status.HTTP_201_CREATED

def create_user(db: Session, user: UserRegisterRequest):
    db_user = UserBackend(username=user.username, password=user.password)
    db_user.hash_password()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user