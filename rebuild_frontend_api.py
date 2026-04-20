import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
cd /var/www/tesis-app/frontend
echo "--- Rebuilding Frontend with explicit API URL ---"
VITE_API_URL=https://api.liqexpert.com npm run build
cp -r dist/* ../backend/static/
echo "--- Rebuild Complete ---"
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
