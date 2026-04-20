import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = "sudo systemctl status tesis-backend"
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
