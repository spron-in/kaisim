import os
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Import routes after app initialization to avoid circular imports
from routes import *  # noqa: E402
