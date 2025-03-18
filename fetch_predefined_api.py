import requests
import json
import urllib3

def fetch_api_responses(api_endpoint, api_paths, bearer_token):
    """
    Fetches responses from specified API endpoints, ignoring TLS certificate validation.

    Returns:
        dict: A dictionary containing API paths and their corresponding responses.
    """

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Disable insecure request warnings

    results = {"entries": []}

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    for api_path in api_paths:
        try:
            response = requests.get("{}{}".format(api_endpoint, api_path), headers=headers, verify=False) # verify=False ignores TLS validation
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                response_json = {"text": response.text} #if the response is not json, saves it as text.

            results["entries"].append({
                "api_path": api_path,
                "response": response_json
            })

        except requests.exceptions.RequestException as e:
            print("api {} failed".format(api_path))

    return results

# Example usage:
api_paths = [
    "/api",
    "/api/v1",
    "/apis",
    "/apis/admissionregistration.k8s.io/v1",
    "/apis/apiextensions.k8s.io/v1",
    "/apis/apiregistration.k8s.io/v1",
    "/apis/apps/v1",
    "/apis/authentication.k8s.io/v1",
    "/apis/authorization.k8s.io/v1",
    "/apis/auto.gke.io/v1",
    "/apis/auto.gke.io/v1alpha1",
    "/apis/autoscaling.x-k8s.io/v1",
    "/apis/autoscaling.x-k8s.io/v1beta1",
    "/apis/autoscaling/v1",
    "/apis/autoscaling/v2",
    "/apis/batch/v1",
    "/apis/certificates.k8s.io/v1",
    "/apis/cloud.google.com/v1",
    "/apis/cloud.google.com/v1beta1",
    "/apis/coordination.k8s.io/v1",
    "/apis/datalayer.gke.io/v1",
    "/apis/discovery.k8s.io/v1",
    "/apis/events.k8s.io/v1",
    "/apis/flowcontrol.apiserver.k8s.io/v1",
    "/apis/flowcontrol.apiserver.k8s.io/v1beta3",
    "/apis/hub.gke.io/v1",
    "/apis/internal.autoscaling.gke.io/v1",
    "/apis/metrics.k8s.io/v1beta1",
    "/apis/monitoring.googleapis.com/v1",
    "/apis/monitoring.googleapis.com/v1alpha1",
    "/apis/networking.gke.io/v1",
    "/apis/networking.gke.io/v1beta1",
    "/apis/networking.gke.io/v1beta2",
    "/apis/networking.k8s.io/v1",
    "/apis/node.gke.io/v1",
    "/apis/node.k8s.io/v1",
    "/apis/nodemanagement.gke.io/v1alpha1",
    "/apis/policy/v1",
    "/apis/rbac.authorization.k8s.io/v1",
    "/apis/scheduling.k8s.io/v1",
    "/apis/snapshot.storage.k8s.io/v1",
    "/apis/snapshot.storage.k8s.io/v1beta1",
    "/apis/storage.k8s.io/v1",
    "/apis/warden.gke.io/v1",
    '/openapi/v3',
    '/openapi/v3/api/v1',
    '/openapi/v2'
]
api_endpoint = '' # Replace with your k8s cluster endpoint
bearer_token = ""  # Replace with your actual bearer token

api_responses = fetch_api_responses(api_endpoint, api_paths, bearer_token)
print(json.dumps(api_responses, indent=4))
