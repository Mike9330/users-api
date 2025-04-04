from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set in the environment variables")

client = MongoClient(MONGO_URI)

db = client["user_db"]  
users_collection = db["users"]  

class UserSignup(BaseModel):
    email: EmailStr 
    password: str

app = FastAPI()

@app.post("/signup")
async def signup(user: UserSignup):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    new_user = {"email": user.email, "password": hashed_password}
    users_collection.insert_one(new_user)
    
    return {"message": "User created successfully", "email": user.email, "password": str(hashed_password)}

@app.get("/users/{email}")
async def get_user(email: str):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"email": user["email"], "password": str(user["password"])}

@app.delete("/delete/{email}")
async def delete_user(email: str):
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}