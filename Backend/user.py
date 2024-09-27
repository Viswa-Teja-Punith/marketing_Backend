from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext
from fastapi import APIRouter

router = APIRouter()

client = MongoClient('mongodb+srv://nani:Nani@cluster0.p71g0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client["Marketing_DB"]
collection = db["User_credentials"]

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class AdminSignUpRequest(BaseModel):
    email: str
    username: str
    password: str

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# @router.post("/usersignup", status_code=201)
@router.post("/usersignup", status_code=201)
async def user_signup(signup_request: AdminSignUpRequest):
    try:
        existing_user = collection.find_one({"$or": [{"email": signup_request.email}, {"username": signup_request.username}]})
        
        if existing_user:
            if existing_user.get('email') == signup_request.email:
                raise HTTPException(status_code=400, detail="Email already registered")
            if existing_user.get('username') == signup_request.username:
                raise HTTPException(status_code=400, detail="Username already taken")

        new_user = {
            "email": signup_request.email,
            "username": signup_request.username,
            "password": hash_password(signup_request.password)
        }
        
        collection.insert_one(new_user)
        return {"message": "User account created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# User Login
# UserLoginRequest model
class UserLoginRequest(BaseModel):
    email: str
    password: str

# Helper function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# User login route
@router.post("/userlogin")
async def user_login(login: UserLoginRequest):
    try:
        user = collection.find_one({"email": login.email})
        
        # Check if the user exists
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify the password
        if not verify_password(login.password, user['password']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # If successful, return a success message
        return {"message": "Login successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
