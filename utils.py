from flask import jsonify, request
from datetime import datetime
from crewai import Crew
from agents import kubernetes_api_agent
from tasks import kubernetes_api_task
import re
import json


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
            return {'valid': False, 'message': 'Invalid JSON body'}

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
            **base_response, 'message':
            f'Successfully retrieved resource at {path}',
            'query_params': dict(request.args)
        }
        return jsonify(response), 200

    elif method == 'POST':
        response = {
            **base_response, 'message':
            f'Successfully created resource at {path}',
            'data': request.get_json()
        }
        return jsonify(response), 201

    elif method == 'PUT':
        response = {
            **base_response, 'message':
            f'Successfully updated resource at {path}',
            'data': request.get_json()
        }
        return jsonify(response), 200

    elif method == 'PATCH':
        response = {
            **base_response, 'message':
            f'Successfully patched resource at {path}',
            'data': request.get_json()
        }
        return jsonify(response), 200

    elif method == 'DELETE':
        response = {
            **base_response, 'message':
            f'Successfully deleted resource at {path}'
        }
        return jsonify(response), 200

    else:
        return jsonify({
            'error': 'Method not supported',
            'method': method,
            'path': path
        }), 405


def simulate_kubernetes_api(request):
    """
    Simulate a Kubernetes API request and return a response
    """

    kubernetes_api_crew = Crew(agents=[kubernetes_api_agent],
                               tasks=[kubernetes_api_task],
                               verbose=True)

    result = kubernetes_api_crew.kickoff(inputs={
        'request_type': request.method,
        'api_endpoint': request.path
    })

    return result.raw


def markdown_json_to_dict(markdown_json):
    """
    Converts a Markdown JSON code block into a Python dictionary.
    """
    # Remove Markdown code block markers
    cleaned_json = re.sub(r"```(?:json)?\n?|```$", "", markdown_json)

    try:
        # Parse the JSON string into a Python dictionary
        data = json.loads(cleaned_json)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None  # Or raise an exception if you prefer
