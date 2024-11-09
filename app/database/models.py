from databases import Database
from sqlalchemy import Column, Integer, Text, String,DateTime, Sequence, func, ForeignKey, create_engine

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from passlib.context import CryptContext

from app.database.config_db import DB_MESSAGE_ADMIN_URL

admin_engine = create_engine(DB_MESSAGE_ADMIN_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBackend(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(Text)
    time_created = Column(DateTime, default=func.now())
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    # def hash_password(self):
    #     self.password = pwd_context.hash(self.password)

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
    

