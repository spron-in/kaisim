
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
        max_retries = 5
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                db.session.rollback()  # Always rollback before retry
                result = func(*args, **kwargs)
                db.session.commit()  # Explicitly commit if successful
                return result
            except OperationalError as e:
                if any(msg in str(e) for msg in ["SSL connection has been closed unexpectedly", "connection already closed"]):
                    if attempt < max_retries - 1:
                        sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                raise
            except Exception:
                db.session.rollback()
                raise
        return func(*args, **kwargs)
    return wrapper

# Add connection check function
def check_connection(app):
    with app.app_context():
        try:
            db.session.execute(db.select(1))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

class APICache(db.Model):
    __tablename__ = 'api_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_id = db.Column(db.UUID, nullable=False, default=uuid.uuid4)
    user_token = db.Column(db.UUID, nullable=True)
    api_path = db.Column(db.String, nullable=False)
    response = db.Column(db.Text, nullable=False)
    is_predefined = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
