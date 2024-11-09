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

@router.post("/register", response_model=User)
async def register(new_user: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Desc: Handle logic register at Backend username
    Problem - SOLVED:
    Status: DONE
    NOTE:
    1. THE RETURN TYPE SHOULD BE VALID AS (PART) THE PATH OF API -> AUTOMATICALLY INTERPRETED AS "QUERY" PARAMETERS
    """
    
    statement = select(UserBackend).filter(UserBackend.username == new_user.username).limit(1)
    # db_user_username = db.execute(statement).scalar().username
    db_user_object = db.execute(statement).scalar()
    if db_user_object:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = UserBackend(username=new_user.username, password=new_user.password)
    db_user.hash_password()
    db.add(db_user)
    db.commit()
    return db_user