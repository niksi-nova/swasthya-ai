from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import bcrypt, os#,jwt

load_dotenv()

app = FastAPI()

# --- CORS for React frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MongoDB setup ---
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
users_collection = db["users"]
SECRET = os.getenv("JWT_SECRET")

# --- Schemas ---
class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.get("/")
def root():
    return {"message": "API is running 🚀"}

# --- SIGNUP ---
@app.post("/signup")
def signup(user: UserSignup):
    existing = users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    users_collection.insert_one({
        "name": user.name,
        "email": user.email,
        "password": hashed
    })
    return {"message": "Signup successful"}

# --- LOGIN ---
@app.post("/login")
def login(user: UserLogin):
    found = users_collection.find_one({"email": user.email})
    if not found:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not bcrypt.checkpw(user.password.encode("utf-8"), found["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({"user_id": str(found["_id"])}, SECRET, algorithm="HS256")
    return {"message": "Login successful", "token": token}