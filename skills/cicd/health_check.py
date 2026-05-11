"""
Skill: Health Check
Verifies that all containers are running and healthy.
"""
import subprocess

def health_check() -> str:
    try:
        cmd = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return f"Health check results:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Health check failed:\n{e.stderr}"
