from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import timedelta
from typing import Optional
from .. import schemas, models, auth_utils
from ..database import get_db
from ..config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    SECRET_KEY, ALGORITHM
)

router = APIRouter()

@router.get("/login")
async def login_google():
    """Initiate Google OAuth2 login"""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        "response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid%20profile%20email"
        "&access_type=offline"
    )
    return RedirectResponse(google_auth_url)

@router.get("/callback")
async def callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth2 callback"""
    # Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        # Get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        user_response = await client.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Check if user exists, create if not
        user = auth_utils.get_user_by_google_id(db, user_info["id"])
        if not user:
            user_create = schemas.UserCreate(
                google_id=user_info["id"],
                email=user_info["email"],
                name=user_info["name"],
                picture=user_info.get("picture")
            )
            user = auth_utils.create_user(db, user_create)
        
        # Create access token
        access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_utils.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Redirect back to frontend with access token
        frontend_redirect_url = f"http://localhost:5173/callback?access_token={access_token}"
        return RedirectResponse(url=frontend_redirect_url)

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}

@router.get("/user", response_model=schemas.User)
async def get_user(request: Request, db: Session = Depends(get_db)):
    """Get current user info"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = auth_utils.get_user_by_email(db, user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )