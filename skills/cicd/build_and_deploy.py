"""
Skill: Optimized Pull and Deploy (VPS) v2.0
Pulls latest images from GHCR and redeploys CFO Expert Agent containers.
Architecture v2.0: Includes notification to Orchestrator.
"""
import subprocess
import os
import logging
from core.ssh_utils import run_remote_command
from skills.monitoring.notify_orchestrator import notify_orchestrator

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
        is_local = os.getenv("DEPLOY_LOCAL", "true").lower() == "true"
        
        notify_orchestrator("🚀 Iniciando despliegue de arquitectura v2.0 en VPS...")

        if is_local:
            logger.info("Executing deployment LOCALLY on VPS.")
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    err_msg = f"Local deploy failed at '{cmd}':\n{result.stderr}"
                    notify_orchestrator(f"❌ Fallo en el despliegue: {cmd}", level="ERROR")
                    return err_msg
                results.append(result.stdout)
        else:
            logger.info("Executing deployment REMOTELY via SSH.")
            for cmd in commands:
                status, out, err = run_remote_command(cmd)
                if status != 0:
                    err_msg = f"SSH deploy failed at '{cmd}':\n{err}"
                    notify_orchestrator(f"❌ Fallo en el despliegue SSH: {cmd}", level="ERROR")
                    return err_msg
                results.append(out)

        success_msg = "✅ Despliegue completado con éxito usando imágenes de GHCR."
        notify_orchestrator(success_msg)
        
        return "Deploy successful using GHCR images.\n" + "\n".join(results[-2:])
    except Exception as e:
        logger.exception("Deploy exception occurred")
        err_msg = f"Deploy failed with exception: {str(e)}"
        notify_orchestrator(f"💥 Error crítico en build_and_deploy: {str(e)}", level="ERROR")
        return err_msg

if __name__ == "__main__":
    print(build_and_deploy())
