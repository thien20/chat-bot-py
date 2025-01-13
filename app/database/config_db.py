from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from passlib.context import CryptContext


import os

load_dotenv()

DB_SUPERUSER_USERNAME = os.getenv("DATABASE_SUPERUSER_USERNAME")
DB_SUPERUSER_PASSWORD = os.getenv("DATABASE_SUPERUSER_PASSWORD")

# ADMIN FOR `chatbot_db`
DB_ADMIN_USERNAME = os.getenv("DATABASE_ADMIN_USERNAME")
DB_ADMIN_PASSWORD = os.getenv("DATABASE_ADMIN_PASSWORD")

DEFAULT_DATABASE_NAME = os.getenv("DEFAULT_DATABASE_NAME")
DB_HOST = os.getenv("DATABASE_HOST")
DB_NAME = os.getenv("DATABASE_NAME")

DB_SUPERUSER_URL = f"postgresql://{DB_SUPERUSER_USERNAME}:{DB_SUPERUSER_PASSWORD}@{DB_HOST}:5432/{DEFAULT_DATABASE_NAME}"
DB_MESSAGE_ADMIN_URL = f"postgresql://{DB_ADMIN_USERNAME}:{DB_ADMIN_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

admin_engine = create_engine(DB_MESSAGE_ADMIN_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
