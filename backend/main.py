from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Google Auth Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
from .middleware.requestloggingmiddleware import RequestLoggingMiddleware
# Add middleware to the app
app.add_middleware(RequestLoggingMiddleware)

@app.get("/")
async def root():
    return {"message": "Google Auth Backend"}