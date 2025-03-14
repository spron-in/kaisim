from flask import request, jsonify
from datetime import datetime
import signal
import uuid
from functools import wraps
from app import app, logger
from utils import validate_request, create_response, simulate_kubernetes_api, markdown_json_to_dict
from models import db, APICache, retry_on_disconnect

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            uuid.UUID(token)
        except ValueError:
            return jsonify({'error': 'Invalid token format - must be UUID'}), 401
            
        return f(*args, **kwargs)
    return decorated


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
            "the endpoint to share all request details, for testing purposes",
            "/cache":
            "provide cached responses to API requests"
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
@require_token
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
        from flask import copy_current_request_context

        try:
            if timeout:
                signal.alarm(int(timeout))
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
            return jsonify(markdown_json_to_dict(raw_simulated_response))
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
        
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


@app.route('/cache', methods=['POST'])
@require_token
def store_cache_entry():
    """Store a cache entry"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    if not data or 'api_path' not in data or 'response' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    auth_token = request.headers.get('Authorization').split(' ')[1]
    try:
        # Check if request tries to create a predefined entry
        if data.get('is_predefined', False):
            return jsonify({'error': 'Users cannot create predefined cache entries'}), 403
            
        cache_entry = APICache(
            user_token=uuid.UUID(auth_token),
            api_path=data['api_path'],
            response=data['response'],
            is_predefined=False  # Explicitly set to False
        )
        db.session.add(cache_entry)
        db.session.commit()
        return jsonify({
            'message': 'Cache entry stored successfully',
            'cache_id': str(cache_entry.cache_id)
        }), 201
    except Exception as e:
        logger.error(f"Error storing cache: {str(e)}")
        return jsonify({'error': 'Failed to store cache entry'}), 500

@app.route('/cache', methods=['GET'])
@require_token
def get_all_cache_entries():
    """Get all cache entries for a user"""
    auth_token = request.headers.get('Authorization').split(' ')[1]
    try:
        cache_entries = APICache.query.filter(
            db.or_(
                APICache.user_token == uuid.UUID(auth_token),
                APICache.is_predefined == True
            )
        ).order_by(APICache.created_at.desc()).all()
        
        entries = [{
            'cache_id': str(entry.cache_id),
            'api_path': entry.api_path,
            'response': entry.response,
            'created_at': entry.created_at.isoformat(),
            'is_predefined': entry.is_predefined
        } for entry in cache_entries]
        
        return jsonify({'entries': entries}), 200
    except Exception as e:
        logger.error(f"Error retrieving cache entries: {str(e)}")
        return jsonify({'error': 'Failed to retrieve cache entries'}), 500

@app.route('/cache/<uuid:cache_id>', methods=['GET'])
@require_token
def get_cache_entry(cache_id):
    """Get a cache entry by its ID"""
    auth_token = request.headers.get('Authorization').split(' ')[1]
    try:
        cache_entry = APICache.query.filter(
            db.and_(
                APICache.cache_id == cache_id,
                db.or_(
                    APICache.user_token == uuid.UUID(auth_token),
                    APICache.is_predefined == True
                )
            )
        ).first()

        if cache_entry:
            cache_response = {
                'api_path': cache_entry.api_path,
                'response': cache_entry.response,
                'created_at': cache_entry.created_at.isoformat(),
                'is_predefined': cache_entry.is_predefined
            }
            return jsonify(cache_response), 200
        return jsonify({'error': 'Cache entry not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving cache: {str(e)}")
        return jsonify({'error': 'Failed to retrieve cache entry'}), 500

@app.route('/cache/<uuid:cache_id>', methods=['DELETE'])
@require_token
def delete_cache_entry(cache_id):
    """Delete a cache entry by its ID"""
    auth_token = request.headers.get('Authorization').split(' ')[1]
    try:
        cache_entry = APICache.query.filter_by(cache_id=cache_id).first()
        
        if not cache_entry:
            return jsonify({'error': 'Cache entry not found'}), 404
            
        if cache_entry.is_predefined:
            return jsonify({'error': 'Cannot delete predefined cache entries'}), 403
            
        if cache_entry.user_token != uuid.UUID(auth_token):
            return jsonify({'error': 'Unauthorized to delete this cache entry'}), 403
            
        db.session.delete(cache_entry)
        db.session.commit()
        
        return jsonify({'message': 'Cache entry deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting cache entry: {str(e)}")
        return jsonify({'error': 'Failed to delete cache entry'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500