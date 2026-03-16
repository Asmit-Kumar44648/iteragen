from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.core.database import supabase

router = APIRouter(prefix="/auth", tags=["auth"])

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    institution: str

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
async def signup(data: SignUpRequest):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.full_name,
                    "institution": data.institution
                }
            }
        })
        if response.user:
            return {
                "message": "Account created. Please verify your email.",
                "user_id": str(response.user.id)
            }
        raise HTTPException(status_code=400, detail="Signup failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin")
async def signin(data: SignInRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        if response.user:
            return {
                "access_token": response.session.access_token,
                "user_id": str(response.user.id),
                "email": response.user.email
            }
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile not found")
