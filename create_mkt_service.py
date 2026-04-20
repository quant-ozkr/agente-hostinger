import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo tee /etc/systemd/system/liq-mkt.service << 'EOF'
[Unit]
Description=LiqExpert Marketing Agency Agent
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=tesis
Group=tesis
WorkingDirectory=/var/www/agencia-mkt
ExecStart=/var/www/agencia-mkt/start.sh
Restart=on-failure
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=liq-mkt

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable liq-mkt
sudo systemctl start liq-mkt
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
