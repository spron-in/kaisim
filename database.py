
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from models import db, APICache
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from app import app

def get_db():
    """Get database connection with pooling"""
    engine = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'],
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections after 30 minutes
        pool_pre_ping=True  # Enable automatic reconnection
    )
    return engine.connect()

def init_db():
    """Initialize database tables"""
    try:
        db.create_all()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

def store_cache(user_token: str, api_path: str, response: str, is_predefined: bool = False):
    """Store cache entry"""
    try:
        cache_entry = APICache(
            cache_id=uuid.uuid4(),
            user_token=user_token,
            api_path=api_path,
            response=response,
            is_predefined=is_predefined
        )
        db.session.add(cache_entry)
        db.session.commit()
        return cache_entry.cache_id
    except Exception as e:
        db.session.rollback()
        print(f"Error storing cache: {str(e)}")
        raise

def get_cache(user_token: str, api_path: str):
    """Get cache entry"""
    try:
        cache_entry = APICache.query.filter(
            (APICache.user_token == user_token) | (APICache.is_predefined == True),
            APICache.api_path == api_path
        ).order_by(APICache.created_at.desc()).first()

        return cache_entry.response if cache_entry else None
    except Exception as e:
        print(f"Error getting cache: {str(e)}")
        raise
