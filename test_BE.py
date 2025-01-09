from app.database.models import UserBackend, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends
from typing import Annotated

db_session = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

statement = select(UserBackend).filter(UserBackend.username == "ccccc").limit(1)
db_user_username = db_session.execute(statement).scalar()

if not db_user_username:
    print("No user found")

else:
    print(db_user_username.username)
    print(db_user_username.password)
# print the username value
# print(type(db_user_username.scalar().username))
