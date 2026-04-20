import os
import paramiko
from dotenv import load_dotenv

env_path = os.path.join(".agents", "skills", "hostinger-tesis-manager", "scripts", ".env")
load_dotenv(dotenv_path=env_path)

def deploy():
    ip = os.getenv("HOSTINGER_IP")
    usuario = os.getenv("HOSTINGER_USER")
    puerto = int(os.getenv("HOSTINGER_PORT", 22))
    llave_ruta = os.getenv("SSH_KEY_PATH")

    print(f"🚀 Iniciando despliegue del Piloto Automático en {ip}...")

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        cliente.connect(ip, port=puerto, username=usuario, key_filename=llave_ruta)
        sftp = cliente.open_sftp()

        # 1. Subir archivos
        print("Subiendo brainstem_mcp.py...")
        sftp.put("brainstem_mcp.py", "/var/www/tesis-app/backend/brainstem_mcp.py")
        
        print("Subiendo tesis-brainstem.service...")
        sftp.put("tesis-brainstem.service", "/tmp/tesis-brainstem.service")
        
        # 2. Mover servicio a /etc/systemd/ y dar permisos
        print("Configurando el servicio en el sistema...")
        comandos = [
            "sudo mv /tmp/tesis-brainstem.service /etc/systemd/system/tesis-brainstem.service",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable tesis-brainstem",
            "sudo systemctl restart tesis-brainstem",
            "sudo systemctl status tesis-brainstem --no-pager | head -n 10"
        ]
        
        for cmd in comandos:
            stdin, stdout, stderr = cliente.exec_command(cmd)
            print(f"Exec: {cmd}\n{stdout.read().decode().strip()}")
            err = stderr.read().decode().strip()
            if err: print(f"Nota/Error: {err}")

        print("\n✅ ¡Despliegue completado! El Cerebro Técnico ya está corriendo en el VPS.")
        sftp.close()
    except Exception as e:
        print(f"❌ Error durante el despliegue: {str(e)}")
    finally:
        cliente.close()

if __name__ == "__main__":
    deploy()
