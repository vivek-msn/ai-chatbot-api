from fastapi import FastAPI, Header, HTTPException, Depends

from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

from pydantic import BaseModel,Field

from typing import Optional

from dotenv import load_dotenv

from google import genai

import os

import jwt

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(
     api_key=os.getenv("GOOGLE_API_KEY")
)

app = FastAPI()

security = HTTPBearer()

SECRET_KEY = "my-super-secret-key"

def create_token(username: str):
     payload ={
          "sub": username
     }

     token = jwt.encode(
          payload,
          SECRET_KEY,
          algorithm="HS256"
     )

     return token

def check_api_key(x_api_key: str = Header(...)):
     if x_api_key != "my-secret-key-123":
          raise HTTPException(
               status_code=401,
               detail="Invalid API Key"
          )
     return x_api_key

class User(BaseModel):
        name:str = Field(min_length=2, max_length=50)
        age:int = Field(ge=18,le=100)
        email: Optional [str] = None

class LoginRequest(BaseModel):
     username: str
     password: str

class Question(BaseModel):
     question: str = Field(min_length=1, max_length=5000)

class ChatRequest(BaseModel):
     session_id: str
     question: str

class Answer(BaseModel):
     answer: str

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

@app.post("/secure")
def secure_api(api_key: str = Depends(check_api_key)):
     return {
          "message": "Access Granted"
     }

@app.post("/login")
def login(data: LoginRequest):
    if data.username != "vivek" or data.password !="12345":
         raise HTTPException(
              status_code=401,
              detail="Invalid credentials"
         )

    token = create_token(data.username)

    return{
         "access_token":token,
         "token_type":"bearer"
    }

chat_history = {}

@app.post("/chat", response_model=Answer)
async def chat(data: ChatRequest):


     history = chat_history.get(data.session_id, [])

     
     history.append({
          "role": "user",
          "parts": [
               {"text": data.question}
          ]
     })


     response = await client.aio.models.generate_content(
          model="gemini-3.1-flash-lite",
          contents=history
     )

     history.append({
          "role": "model",
          "parts": [
               {"text": response.text}
          ]
     })

     chat_history[data.session_id] = history


     return {
          "answer": response.text
     }

     