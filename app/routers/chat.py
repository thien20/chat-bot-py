from app.schemas import ChatRequest
from app.dependency import get_VN_client, get_EN_client
from app.database.models import ChatUserRequest
from app.routers.auth import *

from typing import Annotated

from aiplatform.types import ChatCompletionCreateResponse

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from random import randint

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["post"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
