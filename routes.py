from flask import request, jsonify
from datetime import datetime
from app import app, logger
from utils import validate_request, create_response, simulate_kubernetes_api, markdown_json_to_dict


@app.route('/')
def root():
    """
    Root endpoint showing welcome message and available endpoints
    """
    from flask import make_response
    import json
    from collections import OrderedDict

    response_data = OrderedDict([
        ("message",
         "I'm Kubernetes AI Simulator. I can respond to your kubectl requests with AI generated content. More at https://kais.im"
         ),
        ("endpoints", {
            "/api":
            "simulate kubernetes api requests and get responses generated with AI",
            "/details":
            "the endpoint to share all request details, for testing purposes"
        })
    ])

    response = make_response(json.dumps(response_data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/details', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def request_details():
    """
    Show all details about the incoming request
    """
    # Get Authorization header and clean it for display
    auth_header = request.headers.get('Authorization', '')
    if auth_header.lower().startswith('bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        auth_info = {'type': 'Bearer', 'token': token}
    else:
        auth_info = {'type': None, 'token': None}

    # Build detailed response
    details = {
        'method': request.method,
        'url': request.url,
        'path': request.path,
        'headers': dict(request.headers),
        'query_params': dict(request.args),
        'form_data': dict(request.form),
        'json_data': request.get_json(silent=True),
        'auth': auth_info,
        'content_type': request.content_type,
        'content_length': request.content_length,
        'remote_addr': request.remote_addr,
        'timestamp': datetime.utcnow().isoformat()
    }

    return jsonify(details), 200


@app.route('/api', methods=['GET'])
@app.route('/apis', methods=['GET'])
@app.route('/api/<path:dynamic_path>',
           methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/apis/<path:dynamic_path>', methods=['GET'])
def handle_dynamic_path(dynamic_path=""):
    """
    Handle all requests to dynamic paths under /api/
    Returns appropriate responses based on the HTTP method used
    Supports timeout via ?timeout=Xs query parameter
    """
    try:
        # Get timeout from query parameter (e.g., ?timeout=30s)
        timeout_str = request.args.get('timeout', '')
        timeout = None
        if timeout_str:
            try:
                # Remove 's' suffix if present and convert to float
                timeout = float(timeout_str.rstrip('s'))
                if timeout <= 0:
                    raise ValueError("Timeout must be positive")
            except ValueError:
                return jsonify({
                    'error': 'Invalid timeout value',
                    'message': 'Timeout must be a positive number in seconds (e.g., 30 or 30s)'
                }), 400

        from functools import partial
        from werkzeug.exceptions import TimeoutError
        from flask import copy_current_request_context

        if timeout:
            # Wrap the request processing in a timeout context
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError()

            # Set the timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))

        try:
            # Validate the request
            validation_result = validate_request(request)
            if not validation_result['valid']:
                return jsonify({
                    'error': 'Invalid request',
                    'details': validation_result['message']
                }), 400

            # Log the incoming request
        logger.debug(
            f"Received {request.method} request for path: {dynamic_path}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request data: {request.get_json(silent=True)}")

        raw_simulated_response = simulate_kubernetes_api(request)

        # Process the request based on HTTP method
        return jsonify(markdown_json_to_dict(raw_simulated_response))

    except TimeoutError:
        signal.alarm(0)  # Disable the alarm
        return jsonify({
            'error': 'Timeout',
            'message': f'Request timed out after {timeout} seconds'
        }), 408
    except Exception as e:
        if timeout:
            signal.alarm(0)  # Disable the alarm
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
