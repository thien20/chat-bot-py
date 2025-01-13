from sqlalchemy import Column, Integer, Text, String,DateTime, Sequence, func, datetime

from app.database.config_db import *

class UserBackend(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(Text)
    time_created = Column(DateTime, default=func.now())
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def hash_password(self):
        self.password = pwd_context.hash(self.password)

class ChatUserRequest(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, Sequence('message_id_seq'), primary_key=True, autoincrement=True)
    user_id = Column(Text)
    message = Column(Text)
    language = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    
class ChatUserResponse(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, Sequence('response_id_seq'), primary_key=True)
    user_id = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=func.now())

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    

