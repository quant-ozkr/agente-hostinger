import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = "grep -r 'http' /var/www/tesis-app/frontend/src | head -n 20"
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
