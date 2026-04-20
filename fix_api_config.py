import sys
import os
sys.path.append(os.path.join(os.getcwd(), '.agents', 'skills', 'hostinger-tesis-manager', 'scripts'))
import hostinger_mcp

cmd = """
# 1. Eliminar la configuración redundante
sudo rm /etc/nginx/sites-enabled/tesis-api
sudo rm /etc/nginx/sites-available/tesis-api

# 2. Corregir la configuración de api.liqexpert.com (puerto 8001 y WebSockets)
sudo tee /etc/nginx/sites-available/api.liqexpert.com << 'NGINX'
server {
    server_name api.liqexpert.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSockets support
    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    listen [::]:443 ssl; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/liqexpert.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/liqexpert.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = api.liqexpert.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    listen [::]:80;
    server_name api.liqexpert.com;
    return 404; # managed by Certbot
}
NGINX

# 3. Recargar Nginx
sudo nginx -t && sudo systemctl reload nginx
"""
print(hostinger_mcp.ejecutar_comando_ssh(cmd))
