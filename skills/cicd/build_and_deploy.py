"""
Skill: Optimized Pull and Deploy (VPS)
Pulls latest images from GHCR and redeploys CFO Expert Agent containers.
This avoids local builds on the VPS, saving time and resources.
Supports both local execution (if running on target VPS) and remote execution (via SSH).
"""
import subprocess
import os
import logging
from core.ssh_utils import run_remote_command

logger = logging.getLogger("build-and-deploy")

def build_and_deploy() -> str:
    try:
        # Use Pull-based strategy instead of Build-based
        commands = [
            "cd /opt/cfo-expert-agent && git fetch origin master && git reset --hard origin/master",
            "cd /opt/cfo-expert-agent && docker compose -f docker-compose.vps.yml pull",
            "cd /opt/cfo-expert-agent && docker compose -f docker-compose.vps.yml up -d --remove-orphans",
            "docker ps"
        ]

        results = []
        
        # Check if we should run locally or via SSH
        # Fallback to local if SSH config is missing
        is_local = os.getenv("DEPLOY_LOCAL", "true").lower() == "true"
        
        if is_local:
            logger.info("Executing deployment LOCALLY on VPS.")
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return f"Local deploy failed at '{cmd}':\n{result.stderr}"
                results.append(result.stdout)
        else:
            logger.info("Executing deployment REMOTELY via SSH.")
            for cmd in commands:
                status, out, err = run_remote_command(cmd)
                if status != 0:
                    return f"SSH deploy failed at '{cmd}':\n{err}"
                results.append(out)

        return "Deploy successful using GHCR images.\n" + "\n".join(results[-2:])
    except Exception as e:
        logger.exception("Deploy exception occurred")
        return f"Deploy failed with exception: {str(e)}"
