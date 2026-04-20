import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sed -i 's|FRONTEND_URL=.*|FRONTEND_URL=https://liqexpert.com|' /var/www/tesis-app/backend/.env
sed -i 's|BACKEND_URL=.*|BACKEND_URL=https://liqexpert.com|' /var/www/tesis-app/backend/.env
sudo systemctl restart tesis-backend
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
