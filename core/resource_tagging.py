"""
Resource Tagging for Inf Expert Agent - Gap A9.
Multi-tenancy resource tagging.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("ResourceTagging")


class ResourceType:
    THREAD = "thread"
    CHECKPOINT = "checkpoint"
    STORE = "store"
    TOOL = "tool"
    AGENT = "agent"


class ResourceTagger:
    """Manages resource tagging for multi-tenancy."""
    
    def __init__(self, store=None):
        self.store = store
        self._cache: Dict[str, dict] = {}
    
    def tag_resource(
        self,
        resource_id: str,
        resource_type: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """Tag a resource with tenant and custom tags."""
        key = f"{resource_type}_{resource_id}"
        data = {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "tags": tags or {},
            "updated_at": datetime.now().isoformat()
        }
        
        if self.store:
            try:
                self.store.put(("tags", resource_type), key, data)
            except Exception as e:
                logger.error(f"Error tagging resource: {e}")
        
        self._cache[key] = data
        return data
    
    def find_by_tenant(self, tenant_id: str) -> List[dict]:
        """Find all resources belonging to a tenant."""
        results = []
        if self.store:
            try:
                items = self.store.search(("tags",), limit=1000)
                for item in items:
                    if item.get("value", {}).get("tenant_id") == tenant_id:
                        results.append(item["value"])
            except Exception as e:
                logger.error(f"Error searching by tenant: {e}")
        return results
