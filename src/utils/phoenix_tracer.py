import os
from phoenix.otel import register

def setup_phoenix():
    """
    Registers the application with Arize Phoenix using OpenTelemetry.
    Configures the tracer provider with project name and endpoint.
    """
    # Retrieve configuration from environment
    # Default to local Phoenix server if not specified
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "turbotp-default")
    
    print(f"Initializing Phoenix Tracing for Project: {project_name} to {endpoint}")

    # Register with Phoenix (Auto-instrumentation enabled)
    register(
        project_name=project_name,
        endpoint=endpoint,
        auto_instrument=True
    )
