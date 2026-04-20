import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo tee /etc/systemd/system/tesis-staging.service << 'EOF'
[Unit]
Description=LiqExpert Tesis - STAGING
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=tesis
Group=tesis
WorkingDirectory=/var/www/tesis-staging/backend
ExecStart=/var/www/tesis-staging/backend/start.sh
Restart=on-failure
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=tesis-staging

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tesis-staging
sudo systemctl start tesis-staging
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
