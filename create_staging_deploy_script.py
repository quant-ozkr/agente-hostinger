import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cat <<'EOF' > /var/www/tesis-staging/deploy.sh
#!/bin/bash
set -e
echo "[DEPLOY-STAGING] Iniciando despliegue..."
cd /var/www/tesis-staging
git pull origin staging

echo "[DEPLOY-STAGING] Actualizando Backend..."
cd backend
source venv/bin/activate
pip install --prefer-binary -r requirements.txt
alembic upgrade head

echo "[DEPLOY-STAGING] Compilando Frontend..."
cd ../frontend
npm install
npm run build
cp -r dist/* ../backend/static/

echo "[DEPLOY-STAGING] Reiniciando servicio..."
sudo systemctl restart tesis-staging
echo "[DEPLOY-STAGING] ¡Completado!"
EOF
chmod +x /var/www/tesis-staging/deploy.sh
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
