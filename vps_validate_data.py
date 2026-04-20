import os
import paramiko
from dotenv import load_dotenv

env_path = os.path.join(".agents", "skills", "hostinger-tesis-manager", "scripts", ".env")
load_dotenv(dotenv_path=env_path)

def ejecutar_comando_ssh(comando):
    ip = os.getenv("HOSTINGER_IP")
    usuario = os.getenv("HOSTINGER_USER")
    puerto = int(os.getenv("HOSTINGER_PORT", 22))
    llave_ruta = os.getenv("SSH_KEY_PATH")
    
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        cliente.connect(ip, port=puerto, username=usuario, key_filename=llave_ruta)
        stdin, stdout, stderr = cliente.exec_command(comando)
        exit_status = stdout.channel.recv_exit_status()
        salida = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        return exit_status, salida, error
    except Exception as e:
        return -1, "", str(e)
    finally:
        cliente.close()

def validate_data():
    print("--- FASE 5: VALIDACIÓN DE DATOS ---")
    
    db_user = os.getenv("DB_USER")
    db_name = os.getenv("DB_NAME")
    
    query = """
    SELECT 'users' as tabla, count(*) FROM users
    UNION ALL SELECT 'tenants', count(*) FROM tenants
    UNION ALL SELECT 'simulations', count(*) FROM simulations;
    """
    
    # Ejecutar psql forzando localhost para usar .pgpass
    cmd = f"psql -h localhost -U {db_user} -d {db_name} -c \\\"{query}\\\""
    status, out, err = ejecutar_comando_ssh(cmd)
    
    if status == 0:
        print("Conteos de tablas críticas:")
        print(out)
    else:
        print(f"Error al ejecutar query: {err}")

if __name__ == "__main__":
    validate_data()
