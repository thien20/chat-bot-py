from pydantic import BaseModel
from datetime import datetime

# Define request model -> manage the input request
class ChatRequest(BaseModel):
    """
    ChatRequest model is used to manage the input request
    """
    # id: int
    # user_id: str
    message: str
    # language: str
    # timestamp: datetime

class ChatResponse(BaseModel):
    id: int
    user_id: str
    message: str
    response: str
    timestamp: datetime
    
class User(BaseModel):
    id: int
    username: str
    password: str
    
class UserRegisterRequest(User):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str