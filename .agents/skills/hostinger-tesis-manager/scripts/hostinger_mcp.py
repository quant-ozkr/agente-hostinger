# hostinger_mcp.py  
import os  
import paramiko  
from mcp.server.fastmcp import FastMCP  
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("HostingerDevOpsTesis")

def ejecutar_comando_ssh(comando: str) -> str:
    """Ejecuta un comando SSH en el VPS. Adaptado para puerto 2222 y llaves."""
    ip = os.getenv("HOSTINGER_IP")
    usuario = os.getenv("HOSTINGER_USER", "tesis")
    puerto_str = os.getenv("HOSTINGER_PORT", "2222")
    llave_ruta = os.getenv("SSH_KEY_PATH")

    # Validar que las variables esenciales estén presentes
    if not ip or not usuario:
        return "Error: Faltan variables de entorno (IP o Usuario)."
    
    # Validar que la ruta de la clave SSH esté presente
    if not llave_ruta:
        return "Error: Falta la variable de entorno SSH_KEY_PATH."
    
    # Convertir puerto a entero con manejo de errores
    try:
        puerto = int(puerto_str)
    except ValueError:
        return f"Error: Puerto inválido '{puerto_str}'. Debe ser un número entero."

    cliente = paramiko.SSHClient()
    # Cargar claves de host conocidas para prevenir ataques MITM
    cliente.load_system_host_keys()
    # Si no se encuentra el host, rechazar la conexión en lugar de aceptarla automáticamente
    cliente.set_missing_host_key_policy(paramiko.RejectPolicy())
       
    try:
        # Conectar únicamente usando clave SSH (no se permite autenticación por contraseña)
        cliente.connect(ip, port=puerto, username=usuario, key_filename=llave_ruta)
        stdin, stdout, stderr = cliente.exec_command(comando)
        exit_status = stdout.channel.recv_exit_status()
           
        salida = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
           
        if exit_status != 0:
            return f"Error [{exit_status}]: {error}\nSalida parcial: {salida}"
        return salida if salida else "Comando ejecutado con éxito."
    except Exception as e:
        return f"Excepción SSH: {str(e)}"
    finally:
        cliente.close()

@mcp.tool()  
def verificar_estado_servidor() -> str:  
    """Verifica CPU, RAM y uso de disco. Especial atención al directorio de backups y ChromaDB."""  
    comando = """  
    echo "--- MEMORIA ---" && free -h && \\
    echo "--- DISCO TOTAL ---" && df -h / && \\
    echo "--- DISCO BACKUPS ---" && du -sh /backups/postgres 2>/dev/null || echo 'No backups dir' && \\
    echo "--- DISCO CHROMADB ---" && du -sh /var/www/tesis-app/backend/data/chroma_db 2>/dev/null || echo 'No chroma dir' && \\
    echo "--- CARGA ---" && uptime  
    """  
    return ejecutar_comando_ssh(comando)

@mcp.tool()  
def verificar_servicio(nombre_servicio: str = "tesis-backend") -> str:  
    """  
    Comprueba el estado de un servicio systemd (ej. tesis-backend, nginx, postgresql).  
    Útil para saber si uvicorn o nginx se cayeron.  
    """  
    comando = f"systemctl status {nombre_servicio} --no-pager | head -n 15"  
    return ejecutar_comando_ssh(comando)

@mcp.tool()  
def ejecutar_script_deploy() -> str:  
    """  
    Ejecuta el script de despliegue oficial (deploy.sh) que simula el proceso de CI/CD.  
    Hace git pull, actualiza dependencias y reinicia systemd.  
    """  
    comando = "sudo /var/www/tesis-app/deploy.sh"  
    return ejecutar_comando_ssh(comando)

@mcp.tool()  
def leer_logs_app(fuente: str = "backend", lineas: int = 50) -> str:  
    """  
    Lee logs de la aplicación.  
    fuente puede ser: 'backend' (journalctl uvicorn), 'nginx_error', 'deploy'.  
    """  
    if fuente == "backend":  
        comando = f"journalctl -u tesis-backend -n {lineas} --no-pager"  
    elif fuente == "nginx_error":  
        comando = f"sudo tail -n {lineas} /var/log/nginx/error.log"  
    elif fuente == "deploy":  
        comando = f"tail -n {lineas} /var/log/tesis-deploy.log"  
    else:  
        return "Fuente no válida. Usa 'backend', 'nginx_error' o 'deploy'."  
      
    return ejecutar_comando_ssh(comando)

@mcp.tool()  
def ejecutar_script_mantenimiento(script: str) -> str:  
    """  
    Ejecuta scripts Python dentro del entorno virtual.  
    Útil para 'scripts/verify_schema.py' o 'scripts/ensure_alembic.py'.  
    """  
    comando = f"""  
    cd /var/www/tesis-app/backend  
    source venv/bin/activate  
    python scripts/{script}  
    """  
    return ejecutar_comando_ssh(comando)

if __name__ == "__main__":  
    mcp.run()
