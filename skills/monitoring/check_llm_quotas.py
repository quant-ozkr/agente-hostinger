"""
Skill: Check LLM Quotas
Scans container logs for 429 RESOURCE_EXHAUSTED errors.
"""
from core.ssh_utils import run_remote_command

def check_llm_quotas() -> str:
    # Scan logs of the marketing agent (the one most prone to 429s)
    cmd = "docker logs --tail 200 cfo_agent_api | grep -c 'RESOURCE_EXHAUSTED' || true"
    status, out, err = run_remote_command(cmd)
    
    if status == 0:
        count = int(out.strip()) if out.strip() else 0
        if count > 0:
            return f"Warning: Detected {count} quota errors (429) in recent logs. Consider switching to Groq if not already done."
        else:
            return "LLM Quotas: No recent 429 errors detected."
    else:
        return f"Error checking logs: {err}"

if __name__ == "__main__":
    print(check_llm_quotas())
