"""
Skill: Health Check v2.1
Verifies that all containers are running, endpoints are responsive, and disk space is sufficient.
"""
import subprocess
import requests
import logging
import os
from core.ssh_utils import run_remote_command

logger = logging.getLogger("health-check")

def get_disk_usage() -> int:
    """Returns the % of disk usage on / partition."""
    is_local = os.getenv("DEPLOY_LOCAL", "true").lower() == "true"
    cmd = "df -h / | tail -n 1 | awk '{print $5}' | sed 's/%//'"
    try:
        if is_local:
            out = subprocess.check_output(cmd, shell=True, text=True).strip()
        else:
            status, out, err = run_remote_command(cmd)
            out = out.strip()
        return int(out) if out.isdigit() else 0
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return 0

def health_check() -> str:
    results = []
    
    # 1. Disk Space Check
    usage = get_disk_usage()
    results.append("--- System Metrics ---")
    if usage > 90:
        results.append(f"❌ DISK_CRITICAL: Usage is at {usage}%! Immediate cleanup required.")
    elif usage > 70:
        results.append(f"⚠️ DISK_WARNING: Usage is at {usage}%. Maintenance recommended.")
    else:
        results.append(f"✅ Disk Usage: {usage}%")

    # 2. Basic Docker status
    try:
        cmd = "docker ps --format '{{.Names}}\t{{.Status}}'"
        is_local = os.getenv("DEPLOY_LOCAL", "true").lower() == "true"
        if is_local:
            ps_out = subprocess.check_output(cmd, shell=True, text=True)
        else:
            status, ps_out, err = run_remote_command(cmd)
            
        results.append("\n--- Docker Container Status ---")
        results.append(ps_out)
    except Exception as e:
        results.append(f"Error checking docker status: {e}")

    # 3. Endpoint Checks
    endpoints = {
        "Backend (8001)": "http://localhost:8001/health",
        "MKT Agent (8000)": "http://localhost:8000/health",
        "Orchestrator (8010)": "http://localhost:8010/health"
    }
    
    results.append("\n--- Internal Endpoint Health ---")
    for name, url in endpoints.items():
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                results.append(f"✅ {name}: OK ({resp.json().get('status', 'no-status')})")
            else:
                results.append(f"❌ {name}: FAILED (Status {resp.status_code})")
        except Exception:
            results.append(f"❌ {name}: UNREACHABLE")
            
    return "\n".join(results)

if __name__ == "__main__":
    print(health_check())
