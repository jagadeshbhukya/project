import asyncpg
import redis
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import AsyncGenerator
import uuid

from .config import settings

# PostgreSQL setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # User preferences
    preferences = Column(JSON, default={})
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, default="New Conversation")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Context and metadata
    context_summary = Column(Text)
    context_entities = Column(JSON, default=[])
    context_topics = Column(JSON, default=[])
    message_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    
    # Message metadata
    metadata = Column(JSON, default={})
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class UserMemory(Base):
    __tablename__ = "user_memory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    memory_type = Column(String, nullable=False)  # 'short_term', 'long_term', 'semantic'
    content = Column(Text, nullable=False)
    importance_score = Column(Integer, default=1)  # 1-10 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Memory metadata
    metadata = Column(JSON, default={})

async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    return redis_client

# Memory Store Functions
class MemoryStore:
    @staticmethod
    def store_short_term(user_id: str, key: str, value: str, ttl: int = 3600):
        """Store short-term memory in Redis"""
        redis_client.setex(f"short_term:{user_id}:{key}", ttl, value)
    
    @staticmethod
    def get_short_term(user_id: str, key: str) -> str:
        """Get short-term memory from Redis"""
        return redis_client.get(f"short_term:{user_id}:{key}")
    
    @staticmethod
    def store_conversation_context(conversation_id: str, context: dict, ttl: int = 3600 * 24):
        """Store conversation context in Redis"""
        import json
        redis_client.setex(f"context:{conversation_id}", ttl, json.dumps(context))
    
    @staticmethod
    def get_conversation_context(conversation_id: str) -> dict:
        """Get conversation context from Redis"""
        import json
        data = redis_client.get(f"context:{conversation_id}")
        return json.loads(data) if data else {}

memory_store = MemoryStore()