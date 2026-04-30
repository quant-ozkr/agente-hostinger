# brainstem_mcp.py - Servidor MCP Local del VPS (Cerebro Técnico)
import os
import subprocess
import shlex
from mcp.server.fastmcp import FastMCP

# Inicializar servidor MCP Autónomo en puerto 8004
mcp = FastMCP("LiqExpertBrainstem", port=8004)

def run_local_cmd(cmd: str) -> str:
    """Ejecuta un comando directamente en el shell del VPS de forma segura."""
    try:
        # En producción, si el comando requiere tuberías, shell=True es necesario,
        # pero los inputs deben estar validados antes de llegar aquí.
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error [{e.returncode}]: {e.stderr.strip()}"
    except Exception as e:
        return f"Excepción local: {str(e)}"

@mcp.tool()
def check_cpu() -> str:
    """Verifica el uso de la CPU del servidor."""
    return run_local_cmd("top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'")

@mcp.tool()
def check_ram() -> str:
    """Verifica el uso de RAM del servidor."""
    return run_local_cmd("free -m")

@mcp.tool()
def check_disk() -> str:
    """Verifica el uso del disco duro del servidor."""
    return run_local_cmd("df -h /")

@mcp.tool()
def fetch_logs_backend(lines: int = 50) -> str:
    """Obtiene los últimos logs del backend (LiqExpert)."""
    # Validación simple
    if not isinstance(lines, int) or lines > 1000 or lines < 1:
        return "El número de líneas debe ser entre 1 y 1000."
    return run_local_cmd(f"journalctl -u tesis-backend -n {lines} --no-pager")

@mcp.tool()
def fetch_logs_nginx(lines: int = 50) -> str:
    """Obtiene los últimos logs de error de Nginx."""
    if not isinstance(lines, int) or lines > 1000 or lines < 1:
        return "El número de líneas debe ser entre 1 y 1000."
    return run_local_cmd(f"tail -n {lines} /var/log/nginx/error.log")

@mcp.tool()
def restart_service(service_name: str) -> str:
    """Reinicia un servicio específico en el VPS (ej. tesis-backend)."""
    # Validación estricta para evitar inyección de comandos
    allowed_services = ["tesis-backend", "tesis-brainstem", "tesis-webhook", "nginx", "postgresql"]
    if service_name not in allowed_services:
        return f"Servicio no autorizado. Servicios permitidos: {', '.join(allowed_services)}"
    
    return run_local_cmd(f"sudo systemctl restart {service_name}")

@mcp.tool()
def trigger_backup() -> str:
    """Dispara un backup de la base de datos de forma segura."""
    from datetime import datetime
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    archivo = f"/backups/postgres/manual_{fecha}.sql.gz"
    
    # Crear directorio si no existe (por si acaso)
    run_local_cmd("mkdir -p /backups/postgres")
    cmd = f"pg_dump -U rootAdminLiq liqExpert | gzip > {archivo}"
    res = run_local_cmd(cmd)
    return f"Backup manual solicitado en {archivo}. Resultado: {res if res else 'Éxito'}"

@mcp.tool()
def verify_schema() -> str:
    """Ejecuta el script de verificación de esquema de la base de datos."""
    # Asume que se corre en el entorno del VPS
    return run_local_cmd("cd /var/www/tesis-app/backend && source venv/bin/activate && python scripts/verify_schema.py")

@mcp.tool()
def resolver_bloqueo_puerto(puerto: int) -> str:
    """Libera el puerto si hay un proceso bloqueándolo."""
    if not isinstance(puerto, int) or puerto < 1 or puerto > 65535:
        return "Puerto inválido."
        
    pid = run_local_cmd(f"lsof -t -i:{puerto}")
    if pid and pid.isdigit():
        run_local_cmd(f"kill -9 {pid}")
        return f"Proceso {pid} eliminado del puerto {puerto}."
    return f"No se encontró proceso bloqueando el puerto {puerto}."

if __name__ == "__main__":
    mcp.run(transport="sse")
