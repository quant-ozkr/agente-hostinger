import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
sudo tee /etc/nginx/sites-available/tesis << 'NGINX'
server {
    listen 80;
    server_name liqexpert.com www.liqexpert.com;

    # Frontend (SPA)
    root /var/www/tesis-app/backend/static;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Backend
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSockets
    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Healthcheck
    location /health {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }

    # Docs
    location /docs {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }

    client_max_body_size 10M;
}
NGINX

sudo nginx -t && sudo systemctl reload nginx
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
