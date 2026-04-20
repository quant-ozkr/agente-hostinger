import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo certbot --nginx \
    -d liqexpert.com \
    -d www.liqexpert.com \
    -d staging.liqexpert.com \
    -d api.liqexpert.com \
    --non-interactive \
    --agree-tos \
    -m oscar.tesis.liq@gmail.com \
    --redirect \
    --expand
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
