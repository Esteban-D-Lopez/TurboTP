import os
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation import using_session
from openinference.semconv.trace import SpanAttributes
from opentelemetry import trace
import uuid

def setup_phoenix():
    """Initialize Phoenix tracing with OpenTelemetry."""
    
    # Get Phoenix configuration from environment
    collector_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "turbotp")
    
    # Register Phoenix OTEL
    tracer_provider = register(
        project_name=project_name,
        endpoint=collector_endpoint,
    )
    
    # Instrument LangChain
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    
    print(f"✅ Phoenix tracing enabled: {project_name} → {collector_endpoint}")

def generate_session_id() -> str:
    """Generate a unique session ID for tracking related interactions."""
    return str(uuid.uuid4())

def get_tracer(name: str = __name__):
    """Get an OpenTelemetry tracer instance."""
    return trace.get_tracer(name)

def set_session_attributes(session_id: str, mode: str = None, topic: str = None):
    """
    Set session attributes on the current span.
    
    Args:
        session_id: Unique session identifier
        mode: Optional mode (research, composer, chat)
        topic: Optional topic/query being processed
    """
    current_span = trace.get_current_span()
    if current_span:
        current_span.set_attribute(SpanAttributes.SESSION_ID, session_id)
        if mode:
            current_span.set_attribute("turbotp.mode", mode)
        if topic:
            current_span.set_attribute(SpanAttributes.INPUT_VALUE, topic)

# Export utilities
__all__ = [
    'setup_phoenix',
    'generate_session_id',
    'get_tracer',
    'set_session_attributes',
    'using_session',  # Re-export from openinference
    'SpanAttributes'
]
