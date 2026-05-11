"""
Security Middlewares for Inf Expert Agent.
Reuses implementations from liq-expert-agent.
"""

import re
import hashlib
import logging
from collections import defaultdict

logger = logging.getLogger("SecurityMiddleware")


class PIIBlockedException(Exception):
    pass


class PIIMiddleware:
    """Detects and masks PII with multiple strategies (A13)."""
    
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
    IPV4_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    
    def __init__(self, enabled=True, strategy="mask", hash_salt="inf-expert-salt-2026"):
        self.enabled = enabled
        self.strategy = strategy.lower()
        self.hash_salt = hash_salt
    
    def _hash_value(self, value):
        return hashlib.sha256(f"{self.hash_salt}:{value}".encode()).hexdigest()[:12]
    
    def _apply_strategy(self, text, pii_type, count):
        if self.strategy == "redact":
            return f"[REDACTED_{pii_type.upper()}]"
        elif self.strategy == "block":
            raise PIIBlockedException(f"PII blocked: {pii_type}")
        elif self.strategy == "hash":
            return f"[{pii_type.upper()}_HASH:{self._hash_value(text)}]"
        else:
            if pii_type == "email":
                parts = text.split('@')
                return f"{parts[0][:2]}***@{parts[1]}" if len(parts) == 2 else text
            elif pii_type == "credit_card":
                return f"****-****-****-{text.replace('-', '').replace(' ', '')[-4:]}"
            return f"[REDACTED_{pii_type.upper()}]"
    
    def mmask_text(self, text):
        if not self.enabled or not text:
            return text, {}
        detection_counts = {}
        result = text
        
        email_count = 0
        def replace_email(m):
            nonlocal email_count
            email_count += 1
            return self._apply_strategy(m.group(0), "email", email_count)
        result = self.EMAIL_PATTERN.sub(replace_email, result)
        if email_count > 0:
            detection_counts['emails'] = email_count
        
        cc_count = 0
        def replace_cc(m):
            nonlocal cc_count
            cc_count += 1
            return self._apply_strategy(m.group(0), "credit_card", cc_count)
        result = self.CREDIT_CARD_PATTERN.sub(replace_cc, result)
        if cc_count > 0:
            detection_counts['credit_cards'] = cc_count
        
        logger.warning(f"PII processed ({self.strategy}): {detection_counts}")
        return result, detection_counts


class ModelCallLimitMiddleware:
    """Limits LLM calls per session (C13)."""
    def __init__(self, max_calls=10, enabled=True):
        self.max_calls = max_calls
        self.enabled = enabled
        self.call_counts = defaultdict(int)
    
    def check_limit(self, thread_id):
        if not self.enabled:
            return True
        if self.call_counts.get(thread_id, 0) >= self.max_calls:
            logger.error(f"Model call limit exceeded: {thread_id}")
            return False
        return True
    
    def increment(self, thread_id):
        self.call_counts[thread_id] += 1


class ToolCallLimitMiddleware:
    """Limits tool calls per session (C13)."""
    def __init__(self, max_calls=20, enabled=True):
        self.max_calls = max_calls
        self.enabled = enabled
        self.call_counts = defaultdict(int)
    
    def check_limit(self, thread_id):
        if not self.enabled:
            return True
        if self.call_counts.get(thread_id, 0) >= self.max_calls:
            logger.error(f"Tool call limit exceeded: {thread_id}")
            return False
        return True
    
    def increment(self, thread_id):
        self.call_counts[thread_id] += 1


class SummarizationMiddleware:
    """Summarizes long conversations (C15)."""
    def __init__(self, max_messages=20, max_tokens=8000, enabled=True):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.enabled = enabled
    
    def should_summarize(self, messages):
        if not self.enabled:
            return False, ""
        if len(messages) > self.max_messages:
            return True, f"Messages {len(messages)} > {self.max_messages}"
        return False, ""
    
    def summarize_messages(self, messages):
        if not self.enabled or not messages:
            return messages
        should, reason = self.should_summarize(messages)
        if should:
            logger.info(f"Summarizing: {reason}")
            return messages[-10:]  # Keep last 10
        return messages
