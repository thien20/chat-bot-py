from app.models.schemas import ChatRequest, UserRegisterRequest
from app.database.models import ChatUserRequest, SessionLocal, UserBackend
from app.models.schemas import User
from app.routers.auth import *

from typing import Annotated

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse

# from fastapi.templating import Jinja2Templates
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from random import randint
from .routers import register, chat, auth

import logging

app = FastAPI()

app.include_router(register.router)
app.include_router(chat.router)
app.include_router(auth.router)

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
templates = Jinja2Templates(directory="app/templates")


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
# @app.get("/", response_class=HTMLResponse)
# async def index():
#     with open("app/templates/login.html") as f:
#         return HTMLResponse(content=f.read())

# @app.get("/chat", response_class=HTMLResponse)
# async def chat_page(user: User = Depends(get_current_user)):
#     with open("app/templates/chat.html") as f:
#         return HTMLResponse(content=f.read())

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """
    Render the registration form page.
    PROBLEM: 422 cannot be processible
    """
    return templates.TemplateResponse("register.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Run using: uvicorn app.main:app --reload
