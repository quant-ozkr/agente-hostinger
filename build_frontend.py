import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cd /var/www/tesis-app/frontend
echo "--- Installing dependencies ---"
npm install
echo "--- Building frontend ---"
npm run build
echo "--- Preparing static directory ---"
mkdir -p /var/www/tesis-app/backend/static
echo "--- Copying build artifacts ---"
cp -r dist/* /var/www/tesis-app/backend/static/
echo "--- Done ---"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
