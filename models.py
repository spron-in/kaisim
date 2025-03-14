
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class APICache(db.Model):
    __tablename__ = 'api_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_id = db.Column(db.UUID, nullable=False, default=uuid.uuid4)
    user_token = db.Column(db.UUID, nullable=True)
    api_path = db.Column(db.String, nullable=False)
    response = db.Column(db.Text, nullable=False)
    is_predefined = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
