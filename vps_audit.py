import os
import sys

# Agregar la ruta base al path para poder importar core.ssh_utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.ssh_utils import run_remote_command as ejecutar_comando_ssh

def audit():
    print("--- AUDITORÍA DE VPS v2.0 (Arquitectura Refactorizada) ---")
    
    # 1. Puertos abiertos (ufw)
    print("\n1. Firewall (ufw)...")
    status, out, err = ejecutar_comando_ssh("sudo ufw status verbose")
    print(out if status == 0 else f"Error: {err}")

    # 2. Docker Containers
    print("\n2. Contenedores en Ejecución (Arquitectura v2.0)...")
    cmd = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
    status, out, err = ejecutar_comando_ssh(cmd)
    print(out if status == 0 else f"Error: {err}")

    # 3. Webhook Receiver Service
    print("\n3. Servicio cfo-webhook (Autocuración/CD)...")
    status, out, err = ejecutar_comando_ssh("sudo systemctl status cfo-webhook --no-pager")
    print(out if status == 0 else f"Error: {err}")

    # 4. Verificación de Rutas Críticas
    print("\n4. Rutas Críticas...")
    rutas = ["/opt/cfo-expert-agent", "/opt/cfo-expert-agent/logs", "/opt/cfo-expert-agent/Caddyfile"]
    for r in rutas:
        status, out, err = ejecutar_comando_ssh(f"ls -ld {r}")
        print(f"{r}: {out}")

    # 5. Espacio en disco
    print("\n5. Uso de Disco...")
    status, out, err = ejecutar_comando_ssh("df -h / | tail -n 1")
    print(out)

if __name__ == "__main__":
    audit()
