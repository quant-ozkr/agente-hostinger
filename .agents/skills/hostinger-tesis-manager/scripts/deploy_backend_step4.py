import hostinger_mcp

# 1. Crear el script de inicio start.sh
# 2. Crear el archivo de servicio tesis-backend.service
# 3. Habilitar y arrancar el servicio
cmd = """
cat <<'SCRIPT' > /var/www/tesis-app/backend/start.sh
#!/bin/bash
set -e
cd /var/www/tesis-app/backend
source venv/bin/activate
echo "[STARTUP] Starting uvicorn..."
exec uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8001 \
    --workers 4 \
    --log-level info
SCRIPT
chmod +x /var/www/tesis-app/backend/start.sh

sudo tee /etc/systemd/system/tesis-backend.service << 'EOF'
[Unit]
Description=LiqExpert Backend API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=tesis
Group=tesis
WorkingDirectory=/var/www/tesis-app/backend
ExecStart=/var/www/tesis-app/backend/start.sh
Restart=on-failure
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tesis-backend

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tesis-backend
sudo systemctl start tesis-backend
"""

print(hostinger_mcp.ejecutar_comando_ssh(cmd))
