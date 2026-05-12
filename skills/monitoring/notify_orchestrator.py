"""
Skill: Notify Orchestrator
Sends a notification to the system operator via the Orchestrator's Telegram bridge.
"""
import os
import requests
import logging

logger = logging.getLogger("notify-orchestrator")

def notify_orchestrator(text: str, level: str = "INFO") -> bool:
    """
    Sends a message to the Orchestrator's notification endpoint.
    """
    url = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8010")
    secret = os.getenv("A2A_SHARED_SECRET", "")
    
    if not secret:
        logger.warning("A2A_SHARED_SECRET not set, notification might fail.")
        
    try:
        endpoint = f"{url}/v1/notify"
        payload = {"text": text, "level": level}
        headers = {"X-A2A-Secret": secret}
        
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            logger.info(f"Notification sent: {text[:50]}...")
            return True
        else:
            logger.error(f"Failed to notify orchestrator: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Error notifying orchestrator: {e}")
        return False

if __name__ == "__main__":
    # Test
    notify_orchestrator("Inf-Expert-Agent skill test notification.")
