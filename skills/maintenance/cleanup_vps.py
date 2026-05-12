"""
Skill: Cleanup VPS Disk Space
Performs various cleanup operations to free up disk space on the VPS.
"""
import subprocess
import os
import logging
from core.ssh_utils import run_remote_command
from skills.monitoring.notify_orchestrator import notify_orchestrator

logger = logging.getLogger("cleanup-vps")

def cleanup_vps(deep: bool = False) -> str:
    """
    Performs disk cleanup. 
    If deep=True, it uses 'prune -af' (deletes unused images too).
    If deep=False, it only prunes dangling images and stopped containers.
    """
    is_local = os.getenv("DEPLOY_LOCAL", "true").lower() == "true"
    
    commands = [
        "docker container prune -f",
        "docker volume prune -f"
    ]
    
    if deep:
        commands.append("docker system prune -af")
        notify_orchestrator("🧹 Iniciando LIMPIEZA PROFUNDA de disco en VPS...", level="WARNING")
    else:
        commands.append("docker image prune -f")
        notify_orchestrator("🧹 Iniciando limpieza de mantenimiento de disco en VPS...")

    results = []
    try:
        for cmd in commands:
            if is_local:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                results.append(f"CMD: {cmd}\nOUT: {res.stdout}\nERR: {res.stderr}")
            else:
                status, out, err = run_remote_command(cmd)
                results.append(f"CMD: {cmd}\nOUT: {out}\nERR: {err}")

        summary = "✅ Limpieza de disco completada."
        notify_orchestrator(summary)
        return "\n---\n".join(results)
        
    except Exception as e:
        err_msg = f"❌ Fallo crítico durante limpieza de disco: {str(e)}"
        logger.error(err_msg)
        notify_orchestrator(err_msg, level="ERROR")
        return err_msg

if __name__ == "__main__":
    print(cleanup_vps(deep=True))
