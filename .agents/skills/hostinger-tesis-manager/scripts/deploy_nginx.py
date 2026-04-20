import hostinger_mcp

# 1. Configuración de Nginx para 'tesis'
# - Puerto 80
# - Proxy a 127.0.0.1:8001
# - Frontend static files (preparado)
# - WebSocket support

cmd = """
sudo tee /etc/nginx/sites-available/tesis << 'NGINX'
server {
    listen 8080;
    server_name _;

    # Rutas API
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSockets (Audit streaming)
    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }

    # Healthcheck
    location /health {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
    }

    # Documentación OpenAPI
    location /docs {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
    }

    # Frontend (SPA)
    root /var/www/tesis-app/backend/static;
    index index.html;
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
NGINX

# Habilitar y recargar
sudo ln -sf /etc/nginx/sites-available/tesis /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
"""

print(hostinger_mcp.ejecutar_comando_ssh(cmd))
