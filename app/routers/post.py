from fastapi import Depends, Response, status, HTTPException, APIRouter

from app.schemas import User, ChatRequest
from app.dependency import get_VN_client, get_EN_client
from app.database.models import UserBackend, ChatUserRequest, SessionLocal
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from aiplatform.types import ChatCompletionCreateResponse

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



@router.post("/register")
async def register(new_user: User, db: Session = Depends(get_db)):
    """
    Desc: Handle logic register at Backend username
    Problem: why the `post` method is requiring the args and kwargs as parameters?
    Status: Pending
    """
    statement = select(UserBackend).filter(UserBackend.username == new_user.username).limit(1)
    db_user_username = db.execute(statement).scalar().username
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user_instance = UserBackend(username=new_user.username, password=new_user.password)
    new_user_instance.hash_password()
    
    db.add(new_user_instance)
    db.commit()
    return {"message": "User created successfully"}

# API endpoint for chat
# ASSUME: we load the chat for multi users -> async is needed
# NOTE: WE SHOULD SEPARATE 'reply' and 'payload' funtions--> better tests and debug

@router.post("/chat/{language}")
async def chat(request: ChatRequest, language: str, db: Annotated[Session, Depends(get_db)]):
    try:
        logger.info(f"Received language: {language}")
        response = ""

        # Choose client based on the language parameter
        if language == "en":
            client = get_EN_client()
            messages = [
                {"role": "system", "content": "You are a Vietnamese assistant."},
                {"role": "user", "content": request.message}
            ]
            model_name = "meta-llama/Meta-Llama-3-8B-Instruct"  # Model for English
            response = ""
            for message in client.chat_completion(
                model=model_name,
                messages=messages,
                max_tokens=256,
                stream=True,
            ):
                response += message.choices[0].delta.content

        elif language == "vn":
            client = get_VN_client()
            messages = [
                {"role": "system", "content": "You are a Vietnamese assistant."},
                {"role": "user", "content": request.message}
            ]
            model_name = "kilm"
            response = ""
            response: ChatCompletionCreateResponse = client.chat_completions.create(
            messages=messages,
            model=model_name,
            max_tokens=256
            )
            response = response.choices[0].message.content
        else:
            raise HTTPException(status_code=400, detail="Unsupported language")

        # Check if the message is empty
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")


        db.add(ChatUserRequest(user_id=str(randint(1,100)),
                               language=language, 
                               message=request.message,
                               response=response)
                                # id=ChatUserRequest.id,
                                )
        db.commit()
        # db.refresh(ChatUserRequest)
        
        return {"response": response}

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while processing the request.", "error": str(e)}
        )
