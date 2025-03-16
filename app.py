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
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
