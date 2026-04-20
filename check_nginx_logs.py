import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = "sudo tail -n 20 /var/log/nginx/error.log"
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
