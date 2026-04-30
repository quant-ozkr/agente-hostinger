import os
import sys

# Agregar la ruta base al path para poder importar core.ssh_utils si se corre directamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.ssh_utils import run_remote_command as ejecutar_comando_ssh

def update_startup_chain():
    print("--- FASE 2: ACTUALIZANDO STARTUP CHAIN ---")
    
    # 1. Nuevo start.sh
    nuevo_start_sh = """#!/bin/bash
set -e

cd /var/www/tesis-app/backend
source venv/bin/activate

echo "[STARTUP] Running ensure_alembic.py..."
python scripts/ensure_alembic.py

echo "[STARTUP] Running alembic upgrade head..."
alembic upgrade head

echo "[STARTUP] Running verify_schema.py..."
python scripts/verify_schema.py

echo "[STARTUP] Starting uvicorn..."
exec uvicorn app.main:app \\
    --host 127.0.0.1 \\
    --port 8001 \\
    --workers 4 \\
    --log-level info
"""
    # Escapar comillas y pesos para el comando shell
    comando_start = f"printf '{nuevo_start_sh}' | sudo tee /var/www/tesis-app/backend/start.sh > /dev/null && sudo chmod +x /var/www/tesis-app/backend/start.sh"
    
    status, out, err = ejecutar_comando_ssh(comando_start)
    if status == 0:
        print("✔ start.sh actualizado correctamente.")
    else:
        print(f"✘ Error al actualizar start.sh: {err}")

    # 2. Nuevo service file (con hardening y EnvironmentFile)
    nuevo_service = """[Unit]
Description=LiqExpert Backend API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=tesis
Group=tesis
WorkingDirectory=/var/www/tesis-app/backend
EnvironmentFile=/var/www/tesis-app/backend/.env
ExecStart=/var/www/tesis-app/backend/start.sh
Restart=on-failure
RestartSec=10

# Seguridad: limitar capacidades
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/var/www/tesis-app/backend/logs
ReadWritePaths=/var/www/tesis-app/backend/data/chroma_db

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tesis-backend

[Install]
WantedBy=multi-user.target
"""
    comando_service = f"printf '{nuevo_service}' | sudo tee /etc/systemd/system/tesis-backend.service > /dev/null"
    
    status, out, err = ejecutar_comando_ssh(comando_service)
    if status == 0:
        print("✔ tesis-backend.service actualizado.")
    else:
        print(f"✘ Error al actualizar service: {err}")

    # 3. Recargar y Reiniciar
    print("Reiniciando servicio...")
    ejecutar_comando_ssh("sudo systemctl daemon-reload && sudo systemctl restart tesis-backend")
    status, out, err = ejecutar_comando_ssh("sudo systemctl status tesis-backend --no-pager | head -n 15")
    print(out)

if __name__ == "__main__":
    update_startup_chain()
