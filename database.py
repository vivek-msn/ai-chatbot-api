from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

def get_db():
    db= SessionLocal()

    try:
        yield db

    finally:
        db.close()

# Test database connection
with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print(result.scalar())

print("Database engine created successfully")