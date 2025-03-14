import os
from crewai import Agent
from llms import llm

kubernetes_api_agent = Agent(
    role="Kubernetes API simulator",
    goal="Answer user requests mimicing Kubernetes API",
    backstory="You are an application that mimics Kubernetes API for educational purposes.",
    llm=llm,
    verbose=False,
    allow_delegation=False
)