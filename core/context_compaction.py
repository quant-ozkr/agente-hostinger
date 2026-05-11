"""
Context Compaction for Inf Expert Agent - Gap C8.
Automatically compacts conversation context when it exceeds thresholds.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ContextCompaction")


class ContextCompactionMiddleware:
    """Middleware for automatic context compaction."""
    
    def __init__(
        self,
        llm=None,
        max_tokens: int = 8000,
        max_messages: int = 20,
        context_window: int = 10000,
        enabled: bool = True
    ):
        self.llm = llm
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.context_window = context_window
        self.enabled = enabled
        self.compaction_count = {}
    
    def estimate_tokens(self, messages: List[Any]) -> int:
        total_chars = 0
        for msg in messages:
            if hasattr(msg, 'content'):
                content = msg.content
                if isinstance(content, str):
                    total_chars += len(content)
        return total_chars // 4
    
    def should_compact(self, messages: List[Any]) -> Tuple[bool, str]:
        if not self.enabled or not messages:
            return False, ""
        if len(messages) > self.max_messages:
            return True, f"Message count {len(messages)} exceeds {self.max_messages}"
        estimated_tokens = self.estimate_tokens(messages)
        if estimated_tokens > self.max_tokens:
            return True, f"Tokens {estimated_tokens} > {self.max_tokens}"
        return False, ""
    
    def compact(self, messages: List[Any], thread_id: str = "default") -> List[Any]:
        if not messages or len(messages) <= 6:
            return messages
        recent_messages = messages[-6:]
        from langchain_core.messages import SystemMessage
        summary_message = SystemMessage(content="[Context Summary] Previous conversation summarized.")
        compacted = [summary_message] + recent_messages
        self.compaction_count[thread_id] = self.compaction_count.get(thread_id, 0) + 1
        logger.info(f"Compacted {len(messages)} -> {len(compacted)} for {thread_id}")
        return compacted
    
    def compact_if_needed(
        self,
        messages: List[Any],
        state: Optional[Dict[str, Any]] = None,
        thread_id: str = "default"
    ) -> Tuple[List[Any], bool]:
        should_compact, reason = self.should_compact(messages)
        if not should_compact:
            return messages, False
        logger.info(f"Compaction: {reason}")
        compacted = self.compact(messages, thread_id)
        if state is not None and isinstance(state, dict):
            state['messages'] = compacted
        return compacted, True
