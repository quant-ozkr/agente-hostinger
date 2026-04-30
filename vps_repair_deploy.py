import os
import sys

# Agregar la ruta base al path para poder importar core.ssh_utils si se corre directamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.ssh_utils import run_remote_command as ejecutar_comando_ssh

def repair():
    print("--- INICIANDO REPARACIÓN Y DESPLIEGUE ---")
    # El contenido exacto con LF (\n)
    script_content = """#!/bin/bash
set -e
echo "[DEPLOY] Iniciando despliegue sincronizado..."
cd /var/www/tesis-app
git pull origin main

echo "[DEPLOY] Actualizando Backend..."
cd backend
source venv/bin/activate
pip install --prefer-binary -r requirements.txt
python scripts/ensure_alembic.py
alembic upgrade head
python scripts/verify_schema.py

echo "[DEPLOY] Reiniciando servicios..."
sudo systemctl restart tesis-backend
sudo systemctl restart tesis-brainstem
sudo systemctl restart tesis-webhook

echo "[DEPLOY] Verificando estabilidad..."
sleep 3
systemctl is-active tesis-backend tesis-brainstem tesis-webhook
echo "[DEPLOY] Sincronizacion completada con exito."
"""

    # Subir y dar permisos usando printf para evitar problemas de formato
    comando_script = f"printf '{script_content}' > /tmp/deploy.sh && sudo mv /tmp/deploy.sh /var/www/tesis-app/deploy.sh && sudo chmod +x /var/www/tesis-app/deploy.sh"
    
    status, out, err = ejecutar_comando_ssh(comando_script)
    if status == 0:
        print("✔ deploy.sh creado y permisos asignados correctamente.")
    else:
        print(f"✘ Error al crear deploy.sh: {err}")
        return

    # Configurar Sudoers para que no pida pass
    print("Configurando sudoers...")
    sudo_rules = "tesis ALL=(ALL) NOPASSWD: /bin/systemctl restart tesis-backend, /bin/systemctl restart tesis-brainstem, /bin/systemctl restart tesis-webhook"
    comando_sudoers = f"echo '{sudo_rules}' | sudo tee /etc/sudoers.d/tesis-deploy"
    
    status, out, err = ejecutar_comando_ssh(comando_sudoers)
    if status == 0:
        print("✔ Sudoers configurado.")
    else:
        print(f"✘ Error al configurar sudoers: {err}")

    print("✅ Reparación profunda terminada.")

if __name__ == "__main__":
    repair()
