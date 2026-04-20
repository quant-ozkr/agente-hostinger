import os
import paramiko
from dotenv import load_dotenv

env_path = os.path.join(".agents", "skills", "hostinger-tesis-manager", "scripts", ".env")
load_dotenv(dotenv_path=env_path)

def update_nginx_webhook():
    ip = os.getenv("HOSTINGER_IP")
    usuario = os.getenv("HOSTINGER_USER")
    puerto = int(os.getenv("HOSTINGER_PORT", 22))
    llave_ruta = os.getenv("SSH_KEY_PATH")

    print(f"🔧 Configurando ruta de Webhook en Nginx en {ip}...")

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        cliente.connect(ip, port=puerto, username=usuario, key_filename=llave_ruta)
        
        # 1. Leer configuración actual de Nginx
        # Asumimos que el archivo es /etc/nginx/sites-available/tesis o similar
        # Vamos a buscar el archivo de configuración activo
        stdin, stdout, stderr = cliente.exec_command("ls /etc/nginx/sites-enabled/")
        site_file = stdout.read().decode().strip().split('\n')[0]
        
        if not site_file:
            print("❌ No se encontró archivo de sitio activo en Nginx.")
            return

        conf_path = f"/etc/nginx/sites-available/{site_file}"
        
        # 2. Inyectar la location del webhook antes del último cierre de llave
        location_webhook = """
    # ── Webhook de Autocuración (UptimeRobot) ─────────────────────────────
    location /api/v1/devops/uptime {
        proxy_pass http://127.0.0.1:8003/webhook/uptime;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
"""
        # Usamos sed para insertar antes de la última llave de cierre del bloque server
        # Este comando es quirúrgico: busca la última '}' y pone el texto antes.
        cmd_nginx = f"sudo sed -i '$i {location_webhook}' {conf_path}"
        
        # Nota: Sed con múltiples líneas es complejo, mejor usamos un script python temporal en el VPS
        py_script = f"""
import sys
path = '{conf_path}'
with open(path, 'r') as f:
    lines = f.readlines()

# Buscar la última llave de cierre del bloque server
for i in range(len(lines) - 1, -1, -1):
    if '}}' in lines[i]:
        lines.insert(i, \"\"\"{location_webhook}\"\"\")
        break

with open('/tmp/nginx_new.conf', 'w') as f:
    f.writelines(lines)
"""
        cliente.exec_command(f"python3 -c \"{py_script}\"")
        cliente.exec_command(f"sudo cp /tmp/nginx_new.conf {conf_path} && sudo nginx -t && sudo systemctl reload nginx")
        
        print(f"✅ Nginx actualizado. Ruta disponible en: http://{ip}/api/v1/devops/uptime")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        cliente.close()

if __name__ == "__main__":
    update_nginx_webhook()
