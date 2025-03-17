import os
import logging
from flask import Flask
from models import db

from dotenv import load_dotenv

load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
database_url = os.environ.get('DATABASE_URL')

# Use connection pooling URL
if '-pooler' not in database_url:
    database_url = database_url.replace('.connect.', '-pooler.connect.')

app.config.update(
    SQLALCHEMY_DATABASE_URI=database_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={
        'pool_size': 5,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'max_overflow': 10
    }
)

# Check SSL mode
from urllib.parse import urlparse
db_url = urlparse(database_url)
ssl_required = 'sslmode=require' in (db_url.query.decode() if isinstance(db_url.query, bytes) else db_url.query)
logger.info(f"Database SSL mode required: {ssl_required}")

# Initialize SQLAlchemy
db.init_app(app)
with app.app_context():
    db.create_all()
    # Test database connection
    from models import check_connection
    check_connection(app)


# Define web route
@app.route('/web/')
def web_index():
    return render_template('index.html')


# Import routes after app initialization
from routes import *  # noqa: E402
