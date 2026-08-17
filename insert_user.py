from database import SessionLocal
from models import User

db = SessionLocal()

try:
    user = User(username="vivek")

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"User created: id={user.id}, username={user.username}")

finally:
    db.close()