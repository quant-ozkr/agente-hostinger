import os
import paramiko
from typing import Tuple, Optional
import logging

# Configurar logging básico para auditoría
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ssh_utils")

class SSHConnection:
    """Clase para manejar conexiones SSH seguras con el VPS."""
    
    def __init__(self, ip: str, username: str, key_path: str, port: int = 22):
        self.ip = ip
        self.username = username
        self.key_path = key_path
        self.port = port
        self.client = paramiko.SSHClient()
        
        # HG-01: RejectPolicy en lugar de AutoAddPolicy para evitar MITM
        # Esto requiere que el host esté en el known_hosts del sistema local
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    def connect(self) -> bool:
        """Establece la conexión SSH segura."""
        try:
            logger.info(f"Intentando conectar a {self.username}@{self.ip}:{self.port}...")
            self.client.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                key_filename=self.key_path,
                timeout=15,
                look_for_keys=False,
                allow_agent=False # Prevenir uso de ssh-agent no autorizado
            )
            return True
        except paramiko.ssh_exception.SSHException as e:
            logger.error(f"Fallo de conexión SSH (posible MITM o llave rechazada): {e}")
            return False
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            return False

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """Ejecuta un comando en el servidor remoto y devuelve exit_code, stdout, stderr."""
        if not self.client.get_transport() or not self.client.get_transport().is_active():
            if not self.connect():
                return -1, "", "No se pudo establecer la conexión SSH."
                
        try:
            logger.info(f"Ejecutando comando: {command[:50]}...") # Loguear solo el inicio por seguridad
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            
            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            
            return exit_status, out, err
        except Exception as e:
            logger.error(f"Error al ejecutar comando: {e}")
            return -1, "", str(e)
            
    def close(self):
        """Cierra la conexión SSH."""
        self.client.close()

def get_ssh_connection_from_env() -> Optional[SSHConnection]:
    """Crea una conexión SSH leyendo las credenciales de las variables de entorno."""
    from dotenv import load_dotenv
    
    # Intentar cargar desde varias rutas posibles para flexibilidad
    env_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "..", ".env"),
        os.path.join(".agents", "skills", "hostinger-tesis-manager", "scripts", ".env")
    ]
    
    for path in env_paths:
        if os.path.exists(path):
            load_dotenv(dotenv_path=path)
            break
            
    ip = os.getenv("HOSTINGER_IP")
    usuario = os.getenv("HOSTINGER_USER")
    puerto_str = os.getenv("HOSTINGER_PORT", "22")
    llave_ruta = os.getenv("SSH_KEY_PATH")
    
    if not ip or not usuario or not llave_ruta:
        logger.error("Faltan variables de entorno esenciales (HOSTINGER_IP, HOSTINGER_USER, SSH_KEY_PATH).")
        return None
        
    try:
        puerto = int(puerto_str)
    except ValueError:
        logger.error(f"Puerto inválido '{puerto_str}'.")
        return None
        
    return SSHConnection(ip, usuario, llave_ruta, puerto)

def run_remote_command(command: str) -> Tuple[int, str, str]:
    """Función helper para ejecutar un comando único."""
    conn = get_ssh_connection_from_env()
    if not conn:
        return -1, "", "Error de configuración SSH."
        
    status, out, err = conn.execute_command(command)
    conn.close()
    return status, out, err
