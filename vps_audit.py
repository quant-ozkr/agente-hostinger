import os
import sys

# Agregar la ruta base al path para poder importar core.ssh_utils si se corre directamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.ssh_utils import run_remote_command as ejecutar_comando_ssh


def audit():
    print("--- FASE 1: AUDITORÍA INICIAL DEL VPS ---")
    
    # 1. Puertos abiertos (ufw)
    print("\n1. Verificando Firewall (ufw)...")
    status, out, err = ejecutar_comando_ssh("sudo ufw status verbose")
    if status == 0:
        print(out)
    else:
        print(f"Error al verificar ufw: {err}")

    # 2. Proyecto remmi
    print("\n2. Verificando proyecto 'remmi'...")
    status, out, err = ejecutar_comando_ssh("ls -d /var/www/remmi 2>/dev/null || echo 'No remmi dir'")
    print(f"Directorio remmi: {out}")
    status, out, err = ejecutar_comando_ssh("sudo systemctl list-units --type=service | grep remmi || echo 'No remmi service'")
    print(f"Servicio remmi: {out}")

    # 3. Startup chain tesis-app
    print("\n3. Verificando tesis-app startup chain...")
    status, out, err = ejecutar_comando_ssh("cat /var/www/tesis-app/backend/start.sh 2>/dev/null || echo 'No start.sh'")
    print(f"Contenido start.sh:\n{out}")
    
    status, out, err = ejecutar_comando_ssh("cat /etc/systemd/system/tesis-backend.service 2>/dev/null || echo 'No service file'")
    print(f"Contenido tesis-backend.service:\n{out}")

    # 4. Logs y Logrotate
    print("\n4. Verificando logs y logrotate...")
    status, out, err = ejecutar_comando_ssh("ls /etc/logrotate.d/tesis 2>/dev/null || echo 'No logrotate config for tesis'")
    print(f"Configuración logrotate: {out}")

    # 5. Backups cron
    print("\n5. Verificando crontab del usuario...")
    status, out, err = ejecutar_comando_ssh("sudo crontab -l 2>/dev/null || echo 'No crontab'")
    print(f"Crontab:\n{out}")

if __name__ == "__main__":
    audit()
