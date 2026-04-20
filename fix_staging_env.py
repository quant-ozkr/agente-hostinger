import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
# Add missing SECRET_KEY_REFRESH to Staging .env
echo "SECRET_KEY_REFRESH=$(openssl rand -hex 32)" >> /var/www/tesis-staging/backend/.env
sudo systemctl restart tesis-staging
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
