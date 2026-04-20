import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cat <<'EOF' > /var/www/tesis-app/deploy.sh
#!/bin/bash
set -e
echo "[DEPLOY] Iniciando despliegue de LiqExpert..."
cd /var/www/tesis-app
git pull origin main

echo "[DEPLOY] Actualizando Backend..."
cd backend
source venv/bin/activate
pip install --prefer-binary -r requirements.txt
alembic upgrade head

echo "[DEPLOY] Compilando Frontend..."
cd ../frontend
npm install
npm run build
cp -r dist/* ../backend/static/

echo "[DEPLOY] Reiniciando servicio..."
sudo systemctl restart tesis-backend
echo "[DEPLOY] ¡Despliegue completado con éxito!"
EOF
chmod +x /var/www/tesis-app/deploy.sh

cat <<'EOF' > /var/www/agencia-mkt/deploy.sh
#!/bin/bash
set -e
echo "[DEPLOY] Iniciando despliegue de Agencia MKT..."
cd /var/www/agencia-mkt
git pull origin main

echo "[DEPLOY] Actualizando dependencias..."
source venv/bin/activate
pip install --prefer-binary -r requirements.txt
python3 -c "from database.models import init_db; init_db()"

echo "[DEPLOY] Reiniciando servicio..."
sudo systemctl restart liq-mkt
echo "[DEPLOY] ¡Despliegue completado con éxito!"
EOF
chmod +x /var/www/agencia-mkt/deploy.sh
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
