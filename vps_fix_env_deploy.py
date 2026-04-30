import os
import paramiko
from dotenv import load_dotenv

env_path = os.path.join(".agents", "skills", "hostinger-tesis-manager", "scripts", ".env")
load_dotenv(dotenv_path=env_path)

def fix_env_loading():
    ip = os.getenv("HOSTINGER_IP")
    usuario = os.getenv("HOSTINGER_USER")
    puerto = int(os.getenv("HOSTINGER_PORT", 22))
    llave_ruta = os.getenv("SSH_KEY_PATH")

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        cliente.connect(ip, port=puerto, username=usuario, key_filename=llave_ruta)
        
        # Nuevo contenido de deploy.sh que carga el .env explícitamente
        script_content = "#!/bin/bash\n"
        script_content += "set -e\n"
        script_content += "echo \"[DEPLOY] Iniciando despliegue sincronizado...\"\n"
        script_content += "cd /var/www/tesis-app\n"
        script_content += "git pull origin main\n\n"
        
        script_content += "echo \"[DEPLOY] Cargando variables de entorno...\"\n"
        script_content += "cd backend\n"
        # Esta línea es la clave: carga el .env al entorno de la sesión actual
        script_content += "export $(grep -v '^#' .env | xargs)\n\n"
        
        script_content += "source venv/bin/activate\n"
        script_content += "pip install --prefer-binary -r requirements.txt\n"
        script_content += "python scripts/ensure_alembic.py\n"
        script_content += "alembic upgrade head\n"
        script_content += "python scripts/verify_schema.py\n\n"
        
        script_content += "echo \"[DEPLOY] Reiniciando servicios...\"\n"
        script_content += "sudo systemctl restart tesis-backend\n"
        script_content += "sudo systemctl restart tesis-brainstem\n"
        script_content += "sudo systemctl restart tesis-webhook\n\n"
        
        script_content += "echo \"[DEPLOY] Verificando estabilidad...\"\n"
        script_content += "sleep 3\n"
        script_content += "systemctl is-active tesis-backend tesis-brainstem tesis-webhook\n"
        script_content += "echo \"[DEPLOY] ¡Sincronizacion exitosa con variables cargadas!\"\n"

        # Subir el archivo corregido
        sftp = cliente.open_sftp()
        with sftp.file("/tmp/deploy.sh", "wb") as f:
            f.write(script_content.encode("utf-8"))
        
        cliente.exec_command("sudo mv /tmp/deploy.sh /var/www/tesis-app/deploy.sh && sudo chmod +x /var/www/tesis-app/deploy.sh")
        
        print("✅ Script de despliegue actualizado con carga de variables de entorno.")
        sftp.close()
    finally:
        cliente.close()

if __name__ == "__main__":
    fix_env_loading()
