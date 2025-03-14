from flask import jsonify, request
from datetime import datetime

def validate_request(request):
    """
    Validate incoming requests
    """
    # Check Content-Type for methods that typically include a body
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not request.is_json:
            return {
                'valid': False,
                'message': 'Content-Type must be application/json'
            }
        
        # Verify that the JSON body can be parsed
        try:
            request.get_json()
        except Exception:
            return {
                'valid': False,
                'message': 'Invalid JSON body'
            }

    return {'valid': True}

def create_response(method, path, request):
    """
    Create appropriate response based on the HTTP method
    """
    base_response = {
        'timestamp': datetime.utcnow().isoformat(),
        'path': path,
        'method': method
    }

    if method == 'GET':
        response = {
            **base_response,
            'message': f'Successfully retrieved resource at {path}',
            'query_params': dict(request.args)
        }
        return jsonify(response), 200

    elif method == 'POST':
        response = {
            **base_response,
            'message': f'Successfully created resource at {path}',
            'data': request.get_json()
        }
        return jsonify(response), 201

    elif method == 'PUT':
        response = {
            **base_response,
            'message': f'Successfully updated resource at {path}',
            'data': request.get_json()
        }
        return jsonify(response), 200

    elif method == 'PATCH':
        response = {
            **base_response,
            'message': f'Successfully patched resource at {path}',
            'data': request.get_json()
        }
        return jsonify(response), 200

    elif method == 'DELETE':
        response = {
            **base_response,
            'message': f'Successfully deleted resource at {path}'
        }
        return jsonify(response), 200

    else:
        return jsonify({
            'error': 'Method not supported',
            'method': method,
            'path': path
        }), 405
