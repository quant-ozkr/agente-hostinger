"""
CompositeBackend for Inf Expert Agent - Gap A6.
Path-based routing for memory.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("CompositeBackend")


class CompositeBackend:
    def __init__(self):
        self.backends: list[tuple[tuple, Any, str]] = []
        self.default_backend = None
    
    def add_route(self, pattern: tuple, backend: Any, name: str = "unnamed"):
        self.backends.append((pattern, backend, name))
    
    def set_default_backend(self, backend: Any):
        self.default_backend = backend
    
    def _match_route(self, namespace: Tuple[str, ...]) -> Optional[tuple[Any, str]]:
        for pattern, backend, name in self.backends:
            if len(namespace) == len(pattern):
                if all(p == '*' or p == ns for p, ns in zip(pattern, namespace)):
                    return backend, name
        return self.default_backend, "default" if self.default_backend else (None, None)
    
    def put(self, namespace: Tuple[str, ...], key: str, value: Dict[str, Any]):
        backend, name = self._match_route(namespace)
        if backend:
            backend.put(namespace, key, value)
    
    def get(self, namespace: Tuple[str, ...], key: str) -> Optional[Dict[str, Any]]:
        backend, _ = self._match_route(namespace)
        return backend.get(namespace, key) if backend else None
    
    def search(self, namespace_prefix: Tuple[str, ...], limit: int = 10) -> List[Dict[str, Any]]:
        backend, _ = self._match_route(namespace_prefix)
        if backend and hasattr(backend, 'search'):
            return backend.search(namespace_prefix, limit)
        return []
