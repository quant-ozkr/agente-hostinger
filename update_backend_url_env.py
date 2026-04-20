import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
# Update Backend URL in Tesis App
sed -i 's|BACKEND_URL=.*|BACKEND_URL=https://api.liqexpert.com|' /var/www/tesis-app/backend/.env
sudo systemctl restart tesis-backend

# Update Backend URL in Staging
# (Staging probably needs its own api-staging, but for now we'll keep it as is or use staging.liqexpert.com)
# Actually, let's just focus on production for this explicit subdomain change.
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
