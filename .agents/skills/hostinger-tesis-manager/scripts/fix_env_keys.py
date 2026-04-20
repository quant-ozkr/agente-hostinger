import hostinger_mcp

# 1. Añadir SECRET_KEY_REFRESH al .env
# 2. Reiniciar el servicio
cmd = """
cd /var/www/tesis-app/backend
# Generar una nueva llave si no existe y añadirla
echo "SECRET_KEY_REFRESH=$(openssl rand -hex 32)" >> .env
sudo systemctl restart tesis-backend
"""

print(hostinger_mcp.ejecutar_comando_ssh(cmd))
