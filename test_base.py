# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
import sqlalchemy

Base = declarative_base()


print(sqlalchemy.__version__)
print(Base)
print(Base.metadata)
print(Base.metadata.tables)
print(Base.metadata.sorted_tables)