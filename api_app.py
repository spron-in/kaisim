
from flask import Flask
from routes import register_routes

api_app = Flask('api')
register_routes(api_app)
