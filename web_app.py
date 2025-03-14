
from flask import Flask

web_app = Flask('web')

@web_app.route('/')
def home():
    return "<h1>Hello World</h1>"
