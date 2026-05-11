"""
Skill: Optimized Pull and Deploy (VPS)
Pulls latest images from GHCR and redeploys CFO Expert Agent containers.
This avoids local builds on the VPS, saving time and resources.
"""
from core.ssh_utils import run_remote_command

def build_and_deploy() -> str:
    try:
        # Use Pull-based strategy instead of Build-based
        commands = [
            "cd /opt/cfo-expert-agent && git fetch origin master && git reset --hard origin/master",
            # Login to GHCR if needed (optional if already logged in or public)
            # "docker login ghcr.io -u ... -p ...",
            "cd /opt/cfo-expert-agent && docker compose -f docker-compose.vps.yml pull",
            "cd /opt/cfo-expert-agent && docker compose -f docker-compose.vps.yml up -d --remove-orphans",
            "docker ps"
        ]

        results = []
        for cmd in commands:
            status, out, err = run_remote_command(cmd)
            if status != 0:
                return f"Deploy failed at '{cmd}':\n{err}"
            results.append(out)

        return "Deploy successful using GHCR images.\n" + "\n".join(results[-2:])
    except Exception as e:
        return f"Deploy failed with exception: {str(e)}"
