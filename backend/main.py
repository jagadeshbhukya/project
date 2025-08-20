from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_socketio import SocketManager
from contextlib import asynccontextmanager
import socketio

from .database import init_db, get_db
from .auth import router as auth_router
from .conversations import router as conversations_router
from .websocket import setup_socket_handlers
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Application shutting down")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Personal AI Assistant API",
    description="A sophisticated AI assistant with context retention and personalization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SocketIO
socket_manager = SocketManager(
    app=app,
    cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5173"]
)

# Setup WebSocket handlers
setup_socket_handlers(socket_manager.get_socketio_manager())

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(conversations_router, prefix="/conversations", tags=["Conversations"])

@app.get("/")
async def root():
    return {"message": "Personal AI Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}