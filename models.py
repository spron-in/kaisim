
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from time import sleep

db = SQLAlchemy()

# Add retry logic for handling dropped connections
def retry_on_disconnect(func):
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if "SSL connection has been closed unexpectedly" in str(e):
                    if attempt < max_retries - 1:
                        sleep(retry_delay)
                        db.session.rollback()
                        continue
                raise
        return func(*args, **kwargs)
    return wrapper

# Add event listener to handle disconnects
@event.listens_for(db.engine, "engine_connect")
def ping_connection(connection, branch):
    if branch:
        return

    try:
        connection.scalar(db.select(1))
    except Exception:
        connection.invalidate()

class APICache(db.Model):
    __tablename__ = 'api_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_id = db.Column(db.UUID, nullable=False, default=uuid.uuid4)
    user_token = db.Column(db.UUID, nullable=True)
    api_path = db.Column(db.String, nullable=False)
    response = db.Column(db.Text, nullable=False)
    is_predefined = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
