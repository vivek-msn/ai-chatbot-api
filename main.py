from fastapi import FastAPI, Header, HTTPException, Depends

from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

from pydantic import BaseModel,Field

from typing import Optional

from dotenv import load_dotenv

from google import genai

from datetime import datetime, timedelta, timezone

import os

import jwt

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")

api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(
     api_key=os.getenv("GOOGLE_API_KEY")
)

app = FastAPI()

security = HTTPBearer()


# def check_api_key(x_api_key: str = Header(...)):
#      if x_api_key != "my-secret-key-123":
#           raise HTTPException(
#                status_code=401,
#                detail="Invalid API Key"
#           )
#      return x_api_key

class User(BaseModel):
        name:str = Field(min_length=2, max_length=50)
        age:int = Field(ge=18,le=100)
        email: Optional [str] = None

class Question(BaseModel):
     question: str = Field(min_length=1, max_length=5000)

class ChatRequest(BaseModel):
     session_id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9]+-[0-9]+$")
     question: str = Field(min_length=1,max_length=5000)

class Answer(BaseModel):
     answer: str

class LoginRequest(BaseModel):
     username: str
     password: str


     
def create_token(username: str):
     payload ={
          "sub": username,
          "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
     }

     token = jwt.encode(
          payload,
          SECRET_KEY,
          algorithm="HS256"
     )

     return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
     token = credentials.credentials

     try:
          payload = jwt.decode(
               token,
               SECRET_KEY,
               algorithms=["HS256"]
          )

          return payload

     except jwt.InvalidTokenError:
          raise HTTPException(
               status_code=401,
               detail="Invalid or expired token"
          )


     

@app.post("/login")
async def login(data: LoginRequest):

     if data.username != "vivek" or data.password != "12345":
          raise HTTPException(
               status_code=401,
               detail="Invalid username or password"
          )

     token = create_token(data.username)

     return {
          "access_token": token,
          "token_type": "bearer"
     }

@app.post("/ask",response_model=Answer)
async def ask_ai(data: Question):

     try:

          response = await client.aio.models.generate_content(
               model="gemini-3.1-flash-lite",
               contents=data.question
          )

          return {
               "answer": response.text
          }
     
     except Exception:
          raise HTTPException(
               status_code=500,
               details="AI services not available"
          )
     

@app.get("/")
def home():
    return{"message": "Hello Fast API"}

@app.get("/about")
def about():
    return{"message": "This is First Fast Api Application"}

@app.get("/users/{userid}",
         summary="Get user",
         description="Fetch user information by using user id.",
         tags=["Users"])

def users(userid: int):
    return{"userid": userid,
           "message": f"This is {userid} user"
           }

@app.get("/search")
def search(name:str,limit:int = 10):
    return{
        "name": name,
        "limit": limit
    }

@app.post("/users")
def create_user(user: User):
    return{
        "name": user.name,
        "age": user.age,
        "email": user.email
    }

# @app.post("/user", response_model= UserResponse)
# def add_user(user: User):
#     return  user

# @app.post("/secure")
# def secure_api(api_key: str = Depends(check_api_key)):
#      return {
#           "message": "Access Granted"
#      }

# @app.post("/login")
# def login(data: LoginRequest):
#     if data.username != "vivek" or data.password !="12345":
#          raise HTTPException(
#               status_code=401,
#               detail="Invalid credentials"
#          )

#     token = create_token(data.username)

#     return{
#          "access_token":token,
#          "token_type":"bearer"
#     }

chat_history = {}

MAX_HISTORY = 4

@app.post("/chat", response_model=Answer)
async def chat(
     data: ChatRequest,
     user=Depends(verify_token)
):

     username = user["sub"]

     if not data.session_id.startswith(username + "-"):
          raise HTTPException(
               status_code=403,
               detail="You do not have access to this session"
          )
          
     history = chat_history.get(data.session_id, [])

     # Keep space for current user message + AI response
     history = history[-(MAX_HISTORY - 2):]

     history.append({
          "role": "user",
          "parts": [
               {"text": data.question}
          ]
     })
     #Send only limited history to Gemini 
     response = await client.aio.models.generate_content(
          model="gemini-3.1-flash-lite",
          contents=history
     )

     # Add AI response
     history.append({
          "role": "model",
          "parts": [
               {"text": response.text}
          ]
     })

     # Save only latest MAX_HISTORY messages
     history = history[-MAX_HISTORY:]

     chat_history[data.session_id] = history

     return {
          "answer": response.text
     }

@app.delete("/chat/{session_id}")
async def clear_chat(session_id: str,
          user=Depends(verify_token)
          ):
     
     username = user["sub"]

     if not session_id.startswith(username + "-"):
          raise HTTPException(
               status_code=403,
               detail="You do not have access to this session"
          )

     if session_id not in chat_history:
          raise HTTPException(
               status_code=404,
               detail="Session not found"
          )

     del chat_history[session_id]

     return {
          "message": "Chat history cleared successfully"
     }