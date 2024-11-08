import psycopg2

from psycopg2 import sql
from sqlalchemy import create_engine, text

from app.database.config_db import DB_ADMIN_USERNAME, DB_ADMIN_PASSWORD, DB_NAME, DB_SUPERUSER_URL, DB_MESSAGE_ADMIN_URL

from app.database import models

"""
    - This file will handle the database creation for the chat user
    --> WE WILL RENAME IT IF SCALLING UP
    
    DEBUGGING:
    REASSIGN OWNED BY message_admin TO postgres;
    DROP OWNED BY message_admin;
    DROP USER message_admin;
"""


def create_database_and_user():
    try:
        # Connect as superuser
        print("Connecting as superuser to create database, user, and schema permissions...")
        super_user_engine = create_engine(DB_SUPERUSER_URL)
        with super_user_engine.connect() as conn:
            # conn.autocommit = True
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"Database '{DB_NAME}' created.")
            
            conn.execute(text(f"CREATE USER {DB_ADMIN_USERNAME} WITH PASSWORD '{DB_ADMIN_PASSWORD}'"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_ADMIN_USERNAME}"))
            conn.execute(text(f"GRANT USAGE, CREATE ON SCHEMA public TO {DB_ADMIN_USERNAME}"))
            
            print(f"User '{DB_ADMIN_USERNAME}' created and granted all privileges on '{DB_NAME}'.")
            conn.close()
            
    except Exception as e:
        print("An error occurred while setting up the database and user:", e)
    
def create_tables():
    try:
        print(f"Connecting to '{DB_NAME}' as '{DB_ADMIN_USERNAME}' to set up tables...")
        
        # GRANT ADMIN AS SUPER USER
        admin_engine = create_engine(DB_MESSAGE_ADMIN_URL)
        with admin_engine.connect() as conn:
            conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_ADMIN_USERNAME}"))
            conn.close()
        models.Base.metadata.create_all(admin_engine)
        print("Tables created successfully.")
    except Exception as e:
        print("An error occurred while creating tables:", e)

    
if __name__ == "__main__":
    create_database_and_user()
    create_tables()