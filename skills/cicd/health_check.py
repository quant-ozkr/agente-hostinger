"""
Skill: Health Check v2.0
Verifies that all containers are running and their internal health endpoints are responsive.
"""
import subprocess
import requests
import logging

logger = logging.getLogger("health-check")

def health_check() -> str:
    results = []
    
    # 1. Basic Docker status
    try:
        cmd = "docker ps --format '{{.Names}}\t{{.Status}}'"
        ps_out = subprocess.check_output(cmd, shell=True, text=True)
        results.append("--- Docker Container Status ---")
        results.append(ps_out)
    except Exception as e:
        results.append(f"Error checking docker status: {e}")

    # 2. Endpoint Checks (from inside VPS or via localhost if DEPLOY_LOCAL=true)
    endpoints = {
        "Backend (8001)": "http://localhost:8001/health",
        "MKT Agent (8000)": "http://localhost:8000/health",
        "Orchestrator (8010)": "http://localhost:8010/health"
    }
    
    results.append("--- Internal Endpoint Health ---")
    for name, url in endpoints.items():
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                results.append(f"✅ {name}: OK ({resp.json().get('status', 'no-status')})")
            else:
                results.append(f"❌ {name}: FAILED (Status {resp.status_code})")
        except Exception as e:
            results.append(f"❌ {name}: UNREACHABLE ({str(e)})")
            
    return "\n".join(results)

if __name__ == "__main__":
    print(health_check())
