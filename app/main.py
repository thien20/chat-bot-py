from app.schemas import ChatRequest
from app.dependency import get_VN_client, get_EN_client
from app.database.models import ChatUserRequest, SessionLocal, UserBackend
from app.schemas import User
from app.routers.auth import *

from typing import Annotated

from aiplatform.types import ChatCompletionCreateResponse

from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from jose import JWTError, jwt
from random import randint
from datetime import datetime, timedelta

from .routers import register, chat

import logging

app = FastAPI()

app.include_router(register.router)
app.include_router(chat.router)

# Allow Cross-Origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
# The StaticFiles class is parsing the parent directory of the current file (__file__) and looking for a directory named "app" in it.
# app.mount("/app/templates", StaticFiles(directory="app"), name="templates")
templates = Jinja2Templates(directory="templates")


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


# This is for login
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = db_dependency):
    """"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: int, db: Annotated[Session, Depends(get_db)]):
    query = select([ChatUserRequest]).where(ChatUserRequest.c.user_id == user_id).order_by(ChatUserRequest.c.timestamp.desc())
    result = db.execute(query)
    # result = await database.fetch_all(query)
    return {"history": [dict(row) for row in result]}
    # return {"history": [dict(row) for row in query]}


Instrumentator().instrument(app).expose(app, endpoint="/metrics")
  
# Serve the main HTML file
# @app.get("/", response_class=HTMLResponse)
# async def index():
#     with open("app/static/index.html") as f:
#         html_content = f.read()
#     return HTMLResponse(content=html_content, status_code=200)
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("app/templates/login.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(user: User = Depends(get_current_user)):
    with open("app/templates/chat.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: User):
    """
    Render the registration form page.
    """
    return templates.TemplateResponse("register.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Run using: uvicorn app.main:app --reload
