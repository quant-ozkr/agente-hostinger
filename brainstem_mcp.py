# brainstem_mcp.py - El "Piloto Automático" de LiqExpert (Cerebro Técnico)
import os
import subprocess
from mcp.server.fastmcp import FastMCP

# Inicializar servidor MCP Autónomo
mcp = FastMCP("LiqExpertBrainstem")

def run_local_cmd(cmd: str) -> str:
    """Ejecuta un comando directamente en el shell del VPS."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error [{e.returncode}]: {e.stderr.strip()}"
    except Exception as e:
        return f"Excepción local: {str(e)}"

@mcp.tool()
def self_healing_backend() -> str:
    """Intenta diagnosticar y reiniciar el backend si detecta fallos."""
    status = run_local_cmd("systemctl is-active tesis-backend")
    if status == "active":
        return "El backend ya está activo. No se requiere intervención."
    
    # Intento de reinicio
    log = run_local_cmd("journalctl -u tesis-backend -n 20 --no-pager")
    restart = run_local_cmd("sudo systemctl restart tesis-backend")
    return f"Backend detectado como '{status}'. Reiniciando...\nLog previo:\n{log}\nResultado: {restart}"

@mcp.tool()
def monitor_infraestructura() -> str:
    """Verifica recursos del sistema (CPU, RAM, Disco)."""
    return run_local_cmd("free -h && df -h / && uptime")

@mcp.tool()
def ejecutar_backup_emergencia() -> str:
    """Dispara el backup manual de la base de datos inmediatamente."""
    # Asume que el usuario 'tesis' tiene el .pgpass configurado
    from datetime import datetime
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    archivo = f"/backups/postgres/emergency_manual_{fecha}.sql.gz"
    cmd = f"pg_dump -U rootAdminLiq liqExpert | gzip > {archivo}"
    res = run_local_cmd(cmd)
    return f"Backup manual solicitado en {archivo}. Resultado: {res if res else 'Éxito'}"

@mcp.tool()
def resolver_bloqueo_puerto(puerto: int = 8001) -> str:
    """Libera el puerto si hay un proceso huérfano (zombie)."""
    pid = run_local_cmd(f"lsof -t -i:{puerto}")
    if pid and pid.isdigit():
        run_local_cmd(f"kill -9 {pid}")
        return f"Proceso {pid} eliminado del puerto {puerto}."
    return f"No se encontró proceso bloqueando el puerto {puerto}."

if __name__ == "__main__":
    mcp.run()
