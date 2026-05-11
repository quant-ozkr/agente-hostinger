"""
Langfuse Observability Integration for InfExpert Agent.
Reuses the pattern from liq-expert-agent.
"""
import os
import logging

logger = logging.getLogger("InfObservability")

# Reuse PIIMiddleware logic if available
try:
    from app.core.security_middleware import PIIMiddleware
except ImportError:
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from app.core.security_middleware import PIIMiddleware
    except ImportError:
        PIIMiddleware = None


class LangfuseCallbackHandlerWithPII:
    """Wrapper for Langfuse CallbackHandler with PII anonymization."""
    
    def __init__(self, langfuse_callback, pii_middleware=None):
        self.callback = langfuse_callback
        self.pii_middleware = pii_middleware or (PIIMiddleware(enabled=True) if PIIMiddleware else None)
        
    def _anonymize_text(self, text: str) -> str:
        if not text or not self.pii_middleware:
            return text
        masked, _ = self.pii_middleware.mmask_text(text)
        return masked
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        if hasattr(self.callback, 'on_llm_start'):
            anonymized = [self._anonymize_text(p) if isinstance(p, str) else p for p in prompts]
            return self.callback.on_llm_start(serialized, anonymized, **kwargs)
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        if hasattr(self.callback, 'on_tool_start'):
            anonymized = self._anonymize_text(input_str) if isinstance(input_str, str) else input_str
            return self.callback.on_tool_start(serialized, anonymized, **kwargs)
    
    def __getattr__(self, name):
        return getattr(self.callback, name)


def get_langfuse_callback_handler():
    """
    Returns a Langfuse callback handler for tracing LLM calls.
    Integrates PII anonymization.
    """
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    langfuse_host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    
    if not langfuse_public_key or not langfuse_secret_key:
        logger.warning("Langfuse credentials not configured for InfExpert.")
        return None
    
    try:
        from langfuse import Langfuse
        from langfuse.langchain import CallbackHandler
        
        langfuse = Langfuse(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
            host=langfuse_host
        )
        
        callback = CallbackHandler(
            langfuse=langfuse,
            trace_name="inf-expert-agent",
            version="1.0"
        )
        
        # Wrap with PII
        pii_mw = PIIMiddleware(enabled=True) if PIIMiddleware else None
        wrapped = LangfuseCallbackHandlerWithPII(callback, pii_mw)
        
        logger.info(f"Langfuse initialized for InfExpert. Host: {langfuse_host}")
        return wrapped
        
    except ImportError:
        logger.error("langfuse not installed. pip install langfuse langfuse-langchain")
        return None
    except Exception as e:
        logger.error(f"Error initializing Langfuse for InfExpert: {e}")
        return None


def get_langfuse_config():
    return {
        "public_key": os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        "secret_key": os.getenv("LANGFUSE_SECRET_KEY", ""),
        "host": os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
        "enabled": bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
    }
