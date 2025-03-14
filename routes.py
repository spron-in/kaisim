from flask import request, jsonify
from app import app, logger
from utils import validate_request, create_response

@app.route('/api/<path:dynamic_path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def handle_dynamic_path(dynamic_path):
    """
    Handle all requests to dynamic paths under /api/
    Returns appropriate responses based on the HTTP method used
    """
    try:
        # Validate the request
        validation_result = validate_request(request)
        if not validation_result['valid']:
            return jsonify({
                'error': 'Invalid request',
                'details': validation_result['message']
            }), 400

        # Log the incoming request
        logger.debug(f"Received {request.method} request for path: {dynamic_path}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request data: {request.get_json(silent=True)}")

        # Process the request based on HTTP method
        return create_response(request.method, dynamic_path, request)

    except Exception as e:
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
