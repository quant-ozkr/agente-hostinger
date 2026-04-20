import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

# Solicitar certificados para todos los dominios configurados
# --non-interactive: No pide datos por consola
# --agree-tos: Acepta términos de servicio
# -m: Correo para notificaciones de renovación
cmd = """
sudo certbot --nginx \
    -d liqexpert.com \
    -d www.liqexpert.com \
    -d staging.liqexpert.com \
    --non-interactive \
    --agree-tos \
    -m oscar.tesis.liq@gmail.com \
    --redirect \
    --expand
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
