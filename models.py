from sqlalchemy import Column, Integer, String
from database import Base
# from models import User

# Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__= "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)