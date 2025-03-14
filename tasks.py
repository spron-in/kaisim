from crewai import Task
from agents import kubernetes_api_agent

kubernetes_api_task = Task(
    description=("You received the {request_type} request to the following API endpoint:\n"
                "{api_endpoint}\n\n"
                "You should provide the response as if you are a real Kubernetes API. You can imagine resources as we are doing it for educational purposes.\n"),
    expected_output=("A response to the API request mimicing the response of the real Kubernetes API server\n"),
    agent=kubernetes_api_agent,
)