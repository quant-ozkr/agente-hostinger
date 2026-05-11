"""
Skill: Build and Deploy (VPS)
Rebuilds and redeploys all CFO Expert Agent containers using docker compose.
"""
from core.ssh_utils import run_remote_command

def build_and_deploy() -> str:
    try:
        commands = [
            "cd /opt/cfo-expert-agent && git fetch origin master && git reset --hard origin/master",
            # Despliegue unificado usando el archivo de producción endurecido
            "cd /opt/cfo-expert-agent && docker compose -f docker-compose.vps.yml build --no-cache",
            "cd /opt/cfo-expert-agent && docker compose -f docker-compose.vps.yml up -d --remove-orphans",
            "docker ps"
        ]

        results = []
        for cmd in commands:
            status, out, err = run_remote_command(cmd)
            if status != 0:
                return f"Deploy failed at '{cmd}':\n{err}"
            results.append(out)

        return "Deploy successful and Nginx reloaded.\n" + "\n".join(results[-2:])
    except Exception as e:
        return f"Deploy failed with exception: {str(e)}"
