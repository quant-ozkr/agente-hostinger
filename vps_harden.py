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

def harden():
    print("--- FASE 3: HARDENING Y SEGURIDAD ---")
    
    # 1. Configurar UFW
    print("Configurando UFW...")
    # Aseguramos el puerto SSH actual (22) antes de habilitar
    comandos_ufw = [
        "sudo ufw default deny incoming",
        "sudo ufw default allow outgoing",
        "sudo ufw allow 22/tcp",
        "sudo ufw allow 80/tcp",
        "sudo ufw allow 443/tcp",
        "echo 'y' | sudo ufw enable"
    ]
    
    for cmd in comandos_ufw:
        status, out, err = ejecutar_comando_ssh(cmd)
        print(f"Exec: {cmd} -> {out if status == 0 else err}")

    # 2. Verificar estado final
    status, out, err = ejecutar_comando_ssh("sudo ufw status verbose")
    print("\nEstado final de UFW:")
    print(out)

    # 3. Fail2ban
    print("\nInstalando y configurando fail2ban...")
    ejecutar_comando_ssh("sudo apt update && sudo apt install -y fail2ban")
    
    # Configuración básica para sshd
    jail_local = """[sshd]
enabled = true
port = 22
maxretry = 5
bantime = 3600
"""
    ejecutar_comando_ssh(f"printf '{jail_local}' | sudo tee /etc/fail2ban/jail.local > /dev/null")
    ejecutar_comando_ssh("sudo systemctl restart fail2ban")
    status, out, err = ejecutar_comando_ssh("sudo systemctl status fail2ban --no-pager | head -n 5")
    print(out)

if __name__ == "__main__":
    harden()
