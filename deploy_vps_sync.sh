#!/bin/bash
set -e
echo "[DEPLOY] Iniciando despliegue de LiqExpert (Sync Mode)..."
cd /var/www/tesis-app
git pull origin main

echo "[DEPLOY] Actualizando Backend..."
cd backend
source venv/bin/activate
pip install --prefer-binary -r requirements.txt
python scripts/ensure_alembic.py
alembic upgrade head
python scripts/verify_schema.py

echo "[DEPLOY] Reiniciando servicios (Trinidad Agéntica)..."
sudo systemctl restart tesis-backend
sudo systemctl restart tesis-brainstem
sudo systemctl restart tesis-webhook

echo "[DEPLOY] Verificando estabilidad..."
sleep 3
systemctl is-active tesis-backend tesis-brainstem tesis-webhook

echo "[DEPLOY] ¡Sincronización total completada con éxito!"
