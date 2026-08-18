from database import engine, Base
from models import User, ChatSession ,ChatMessage

Base.metadata.create_all(bind=engine)

print("Table created successfully!")