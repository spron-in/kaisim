
from flask import Flask, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from api_app import api_app
from web_app import web_app

app = Flask(__name__)

# Route requests based on host
def host_dispatch(environ, start_response):
    host = environ.get('HTTP_HOST', '')
    if host.startswith('api.'):
        return api_app(environ, start_response)
    return web_app(environ, start_response)

application = DispatcherMiddleware(host_dispatch)

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, application, use_reloader=True)
