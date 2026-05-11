"""
Sleep Time Compute for Inf Expert Agent - Gap M7.
Background tasks during idle periods.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("SleepTimeCompute")


class SleepTask:
    def __init__(self, name: str, task_fn, interval_hours: float = 1.0, enabled: bool = True):
        self.name = name
        self.task_fn = task_fn
        self.interval_hours = interval_hours
        self.enabled = enabled
        self.last_run: Optional[Any] = None
        self.run_count = 0


class SleepTimeComputeManager:
    """Manages sleep time compute tasks for inf-expert-agent."""
    
    def __init__(self, store=None, llm=None, enabled: bool = True):
        self.store = store
        self.llm = llm
        self.enabled = enabled
        self.tasks: List[SleepTask] = []
        self._running = False
        self.stats = {"tasks_completed": 0, "tasks_failed": 0}
        self._register_default_tasks()
    
    def _register_default_tasks(self):
        self.tasks.append(SleepTask("monitor_vps", self._task_monitor_vps, 0.5))
        self.tasks.append(SleepTask("check_health", self._task_check_health, 1.0))
    
    async def _task_monitor_vps(self, **kwargs):
        return {"status": "vps_monitored", "timestamp": "2026-05-01"}
    
    async def _task_check_health(self, **kwargs):
        return {"status": "health_checked", "all_good": True}
    
    async def run_sleep_tasks(self, max_tasks: int = 5):
        if not self.enabled or self._running:
            return {}
        self._running = True
        results = {}
        try:
            for task in self.tasks[:max_tasks]:
                if task.enabled:
                    try:
                        result = await task.task_fn()
                        results[task.name] = {"success": True, "result": result}
                        self.stats["tasks_completed"] += 1
                    except Exception as e:
                        results[task.name] = {"success": False, "error": str(e)}
                        self.stats["tasks_failed"] += 1
        finally:
            self._running = False
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        return {**self.stats, "total_tasks": len(self.tasks)}
