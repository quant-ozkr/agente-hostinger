# Plan de Migración: Railway → Hostinger VPS (Corregido)

> **Estado**: Pendiente de implementación
> **Fecha**: 2026-03-16
> **Origen**: Plan original auditado y corregido — 4 problemas críticos resueltos
> **Prioridad**: Baja (Railway funciona bien para tesis; migrar solo si el costo lo justifica)

---

## 1. Principios de la migración

1. **CI/CD se mantiene intacto** — GitHub Actions sigue corriendo tests; solo cambia el step de deploy (`railway up` → `ssh + deploy script`)
2. **Startup chain idéntica** — `ensure_alembic.py → alembic upgrade head → verify_schema.py → uvicorn` se preserva tal cual
3. **Seguridad del VPS es responsabilidad nuestra** — firewall, SSH hardening, backups a storage externo, actualizaciones automáticas
4. **Zero-downtime** — el usuario nunca debe ver un error durante un deploy

---

## 2. Arquitectura objetivo

```
Internet
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│  Hostinger VPS (Ubuntu 22.04, KVM 4, 8GB RAM)               │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  Nginx (puerto 80/443)                              │     │
│  │  ├─ /                    → static files (React SPA) │     │
│  │  ├─ /api/v1/*            → proxy uvicorn :8001      │     │
│  │  ├─ /api/v1/ws/*         → proxy WebSocket :8001    │     │
│  │  ├─ /health              → proxy uvicorn :8001      │     │
│  │  └─ SSL via Let's Encrypt (auto-renew)              │     │
│  └─────────────────────────────────────────────────────┘     │
│                         │                                    │
│              ┌──────────┴──────────┐                         │
│              ▼                     ▼                         │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  uvicorn :8001   │  │  PostgreSQL 15   │                 │
│  │  FastAPI backend │  │  localhost:5432  │                 │
│  │  4 workers       │  │  (solo local)    │                 │
│  │  user: tesis     │  │  user: app       │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  ChromaDB        │  │  Backups cron    │                 │
│  │  data/chroma_db/ │  │  pg_dump → gzip  │                 │
│  │  (embedded)      │  │  → S3/externo    │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  Firewall (ufw): solo 22(SSH), 80, 443 abiertos             │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Implementación por fases

### Fase 1 — Provisión y hardening del VPS

#### 1.1 — Adquirir VPS

- Plan recomendado: KVM 4 (8GB RAM, 4 vCPU, 200GB SSD)
- OS: Ubuntu 22.04 LTS
- Datacenter: lo más cercano a los usuarios (Miami o Sao Paulo para Colombia)

#### 1.2 — Primer acceso y usuario dedicado

```bash
# Conectar como root
ssh root@IP_DEL_VPS

# Actualizar sistema
apt update && apt upgrade -y

# Crear usuario dedicado (NO usar www-data ni root para la app)
adduser tesis
usermod -aG sudo tesis

# Configurar SSH key para el usuario tesis
su - tesis
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# Pegar tu public key:
echo "ssh-rsa AAAA..." >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

#### 1.3 — SSH hardening

```bash
# Editar /etc/ssh/sshd_config
# Cambiar o verificar estas líneas:

Port 2222                         # Puerto no estándar (evita scanners automáticos)
PermitRootLogin no                # Prohibir login como root
PasswordAuthentication no         # Solo SSH keys
PubkeyAuthentication yes
MaxAuthTries 3
AllowUsers tesis                  # Solo este usuario puede entrar

# Reiniciar SSH
systemctl restart sshd
```

**IMPORTANTE**: Antes de cerrar la sesión root, verificar que puedes entrar como `tesis` por el puerto nuevo:
```bash
ssh -p 2222 tesis@IP_DEL_VPS
```

#### 1.4 — Firewall (ufw)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp comment 'SSH custom port'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
# PostgreSQL NO se abre — solo localhost
# Redis NO se abre — solo localhost (si se instala)
sudo ufw enable
sudo ufw status verbose
```

#### 1.5 — Fail2ban (protección brute-force)

```bash
sudo apt install -y fail2ban

# Crear config local
sudo tee /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = 2222
maxretry = 3
bantime = 3600
findtime = 600
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### 1.6 — Actualizaciones automáticas de seguridad

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
# Seleccionar "Yes" para habilitar actualizaciones automáticas
```

---

### Fase 2 — Instalar servicios base

#### 2.1 — PostgreSQL 15

```bash
sudo apt install -y postgresql-15 postgresql-contrib

# Verificar que solo escucha en localhost
grep listen_addresses /etc/postgresql/15/main/postgresql.conf
# Debe decir: listen_addresses = 'localhost'
# Si dice '*', cambiarlo a 'localhost' y reiniciar

# Crear usuario y base de datos
sudo -u postgres psql << 'EOF'
CREATE USER app WITH PASSWORD 'CONTRASEÑA_SEGURA_AQUI';
CREATE DATABASE tesis_master OWNER app;
GRANT ALL PRIVILEGES ON DATABASE tesis_master TO app;
\q
EOF
```

#### 2.2 — Python 3.11

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip

# Dependencias de sistema para psycopg2 y compilación
sudo apt install -y gcc libpq-dev python3.11-dev
```

#### 2.3 — Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
```

#### 2.4 — Git

```bash
sudo apt install -y git
```

---

### Fase 3 — Migrar base de datos

#### 3.1 — Exportar de Railway

Obtener credenciales de Railway (dashboard → PostgreSQL → Variables):

```bash
# Desde tu máquina local o desde el VPS:
PGPASSWORD='CONTRASEÑA_RAILWAY' pg_dump \
  -h centerbeam.proxy.rlwy.net \
  -p 22101 \
  -U postgres \
  -d railway \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  > railway_backup_$(date +%Y%m%d).sql
```

Notas:
- `--no-owner --no-acl`: evita problemas de permisos al importar con usuario diferente
- `--clean --if-exists`: permite re-importar sin errores si se ejecuta más de una vez
- Verificar el tamaño del dump — si es muy grande, usar `pg_dump ... | gzip > backup.sql.gz`

#### 3.2 — Importar en el VPS

```bash
# Copiar el backup al VPS
scp -P 2222 railway_backup_*.sql tesis@IP_DEL_VPS:/tmp/

# En el VPS: importar
sudo -u postgres psql tesis_master < /tmp/railway_backup_*.sql

# Verificar tablas importadas
sudo -u postgres psql tesis_master -c "\dt public.*"
# Debe mostrar: tenants, users, simulations, wallet_transactions,
# promoters, customer_affiliations, commission_transactions, etc.

# Verificar que alembic_version existe y tiene la revisión correcta
sudo -u postgres psql tesis_master -c "SELECT * FROM alembic_version;"
```

#### 3.3 — Verificar integridad

```bash
# Contar registros en tablas críticas (comparar con Railway)
sudo -u postgres psql tesis_master << 'EOF'
SELECT 'tenants' as tabla, count(*) FROM tenants
UNION ALL SELECT 'users', count(*) FROM users
UNION ALL SELECT 'simulations', count(*) FROM simulations
UNION ALL SELECT 'wallet_transactions', count(*) FROM wallet_transactions;
EOF
```

---

### Fase 4 — Desplegar backend

#### 4.1 — Clonar repositorio

```bash
sudo mkdir -p /var/www
sudo chown tesis:tesis /var/www

# Como usuario tesis:
cd /var/www
git clone https://github.com/TU_USUARIO/mvp_tesis_master.git tesis-app
cd tesis-app/backend
```

#### 4.2 — Entorno virtual y dependencias

```bash
python3.11 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install --prefer-binary -r requirements.txt
pip install --prefer-binary -r requirements-rag.txt   # ChromaDB, grpcio, etc.
```

Nota: `requirements-rag.txt` es **obligatorio** para que el RAG/ChromaDB funcione.
En el Dockerfile actual ambos se instalan — el VPS debe replicar esto.

#### 4.3 — Variables de entorno

```bash
# Crear archivo .env en /var/www/tesis-app/backend/
cat > /var/www/tesis-app/backend/.env << 'EOF'
# ── Database ──────────────────────────────────────────────────────────────
DATABASE_URL=postgresql://app:CONTRASEÑA_SEGURA_AQUI@localhost:5432/tesis_master

# ── Security ──────────────────────────────────────────────────────────────
SECRET_KEY=GENERAR_CON_openssl_rand_hex_64
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── URLs ──────────────────────────────────────────────────────────────────
FRONTEND_URL=https://tu-dominio.com
BACKEND_URL=https://tu-dominio.com

# ── APIs externas ─────────────────────────────────────────────────────────
GEMINI_API_KEY=xxx
GROQ_API_KEY=xxx

# ── LLM ───────────────────────────────────────────────────────────────────
LLM_PROVIDER=groq

# ── MercadoPago (cuando se implemente) ────────────────────────────────────
# MERCADO_PAGO_ACCESS_TOKEN=xxx
# MERCADO_PAGO_WEBHOOK_SECRET=xxx
# ALLOW_MOCK_RELOAD=false
EOF

# Proteger el archivo
chmod 600 /var/www/tesis-app/backend/.env
```

#### 4.4 — Verificar startup chain completa

Probar la misma cadena que ejecuta Railway, manualmente:

```bash
cd /var/www/tesis-app/backend
source venv/bin/activate

# 1. ensure_alembic (crea tabla alembic_version si no existe)
python scripts/ensure_alembic.py

# 2. Migraciones
alembic upgrade head

# 3. Verificación de schema (falla con exit 1 si hay columnas faltantes)
python scripts/verify_schema.py

# 4. Test rápido — arrancar uvicorn y verificar /health
uvicorn app.main:app --host 127.0.0.1 --port 8001 &
sleep 5
curl -s http://127.0.0.1:8001/health | python -m json.tool
# Debe retornar: {"status": "healthy", "database": "connected", "schema": "ok"}

# Detener uvicorn de prueba
kill %1
```

#### 4.5 — Script de startup

Crear un script que encapsule toda la cadena (reutilizado por systemd y por deploys):

```bash
cat > /var/www/tesis-app/backend/start.sh << 'SCRIPT'
#!/bin/bash
set -e

cd /var/www/tesis-app/backend
source venv/bin/activate

echo "[STARTUP] Running ensure_alembic.py..."
python scripts/ensure_alembic.py

echo "[STARTUP] Running alembic upgrade head..."
alembic upgrade head

echo "[STARTUP] Running verify_schema.py..."
python scripts/verify_schema.py

echo "[STARTUP] Starting uvicorn..."
exec uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8001 \
    --workers 4 \
    --log-level info
SCRIPT

chmod +x /var/www/tesis-app/backend/start.sh
```

#### 4.6 — Systemd service

```bash
sudo tee /etc/systemd/system/tesis-backend.service << 'EOF'
[Unit]
Description=LiqExpert Backend API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=tesis
Group=tesis
WorkingDirectory=/var/www/tesis-app/backend
ExecStart=/var/www/tesis-app/backend/start.sh
Restart=on-failure
RestartSec=10

# Seguridad: limitar capacidades del proceso
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/var/www/tesis-app/backend/logs
ReadWritePaths=/var/www/tesis-app/backend/data/chroma_db

# Logs van a journald
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tesis-backend

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tesis-backend
sudo systemctl start tesis-backend

# Verificar que arrancó
sudo systemctl status tesis-backend
sudo journalctl -u tesis-backend -f --no-pager -n 50
```

#### 4.7 — Crear directorios con permisos correctos

```bash
# El usuario tesis debe ser dueño de todo
sudo chown -R tesis:tesis /var/www/tesis-app

# Crear directorio de logs si no existe
mkdir -p /var/www/tesis-app/backend/logs

# ChromaDB persistence
mkdir -p /var/www/tesis-app/backend/data/chroma_db
```

---

### Fase 5 — Nginx como reverse proxy

#### 5.1 — Configuración completa

```bash
sudo tee /etc/nginx/sites-available/tesis << 'NGINX'
# ==============================================================================
# LiqExpert — Nginx Reverse Proxy
# ==============================================================================
# Sirve:
#   - Static files (React SPA) directamente desde Nginx (rápido)
#   - /api/v1/* → proxy a uvicorn :8001
#   - /api/v1/ws/* → proxy WebSocket a uvicorn :8001
#   - /health → proxy a uvicorn :8001
#   - SSL via Let's Encrypt (certbot lo agrega automáticamente)
# ==============================================================================

server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    # Certbot reemplazará esto con redirect a HTTPS automáticamente

    # ── Frontend SPA (React build) ────────────────────────────────────────
    root /var/www/tesis-app/backend/static;
    index index.html;

    # Rutas SPA: cualquier path que no sea archivo ni API → index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # ── Backend API ───────────────────────────────────────────────────────
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts generosos para cálculos complejos y generación de PDFs
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }

    # ── WebSocket (auditoría IA streaming) ────────────────────────────────
    # Ruta real: /api/v1/ws/audit (montado como api_router prefix="/ws")
    location /api/v1/ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeout (mantener conexión abierta durante streaming)
        proxy_read_timeout 300s;
    }

    # ── Healthcheck ───────────────────────────────────────────────────────
    location /health {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ── OpenAPI docs ──────────────────────────────────────────────────────
    location /docs {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }

    # ── Seguridad headers ─────────────────────────────────────────────────
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # ── Limitar tamaño de upload (para PDFs y requests grandes) ───────────
    client_max_body_size 10M;
}
NGINX

# Habilitar site y verificar config
sudo ln -sf /etc/nginx/sites-available/tesis /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

#### 5.2 — Verificar que todo rutea correctamente

```bash
# Desde el VPS:
curl -s http://localhost/health              # → {"status": "healthy", ...}
curl -s http://localhost/api/v1/wallet/status # → {"detail": "Not authenticated"} (401)
curl -s http://localhost/                     # → HTML del React SPA
curl -s http://localhost/dashboard            # → HTML del React SPA (SPA routing)
```

---

### Fase 6 — DNS y SSL

#### 6.1 — Registros DNS

En el panel de tu registrador de dominio (Hostinger, Cloudflare, etc.):

| Tipo | Nombre | Valor | TTL |
|---|---|---|---|
| A | `@` | IP_DEL_VPS | 300 |
| A | `www` | IP_DEL_VPS | 300 |

Esperar propagación DNS (5-30 min):
```bash
dig +short tu-dominio.com
# Debe retornar la IP del VPS
```

#### 6.2 — SSL con Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx

# Generar certificado (certbot modifica la config de Nginx automáticamente)
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

Certbot:
- Agrega redirect HTTP → HTTPS automáticamente
- Configura cron para renovar cada 60 días
- Modifica el bloque `server` de Nginx para escuchar en 443 con SSL

---

### Fase 7 — CI/CD adaptado (GitHub Actions → SSH deploy)

**Este es el cambio más importante vs. el plan original.**

Los tests siguen corriendo en GitHub Actions exactamente igual. Solo cambia el step de deploy.

#### 7.1 — Crear deploy key en el VPS

```bash
# En el VPS, como usuario tesis:
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -N ""
cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/deploy_key
# Copiar la private key → GitHub Secrets: VPS_SSH_KEY
```

#### 7.2 — GitHub Secrets nuevos

| Secret | Valor |
|---|---|
| `VPS_HOST` | IP del VPS |
| `VPS_PORT` | `2222` (puerto SSH custom) |
| `VPS_USER` | `tesis` |
| `VPS_SSH_KEY` | Contenido de `~/.ssh/deploy_key` (private key) |

#### 7.3 — Script de deploy en el VPS

```bash
cat > /var/www/tesis-app/deploy.sh << 'DEPLOY'
#!/bin/bash
# ==============================================================================
# Deploy script — ejecutado por GitHub Actions via SSH
# ==============================================================================
# Réplica del flujo de Railway:
#   git pull → pip install → ensure_alembic → alembic upgrade → verify_schema → restart
# ==============================================================================
set -e

APP_DIR="/var/www/tesis-app"
BACKEND_DIR="$APP_DIR/backend"
LOG="/var/log/tesis-deploy.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') [DEPLOY] Starting..." | tee -a "$LOG"

cd "$BACKEND_DIR"

# 1. Pull cambios
echo "[DEPLOY] git pull..." | tee -a "$LOG"
git pull origin main 2>&1 | tee -a "$LOG"

# 2. Instalar dependencias (solo si requirements cambió)
echo "[DEPLOY] pip install..." | tee -a "$LOG"
source venv/bin/activate
pip install --prefer-binary -q -r requirements.txt 2>&1 | tee -a "$LOG"
pip install --prefer-binary -q -r requirements-rag.txt 2>&1 | tee -a "$LOG"

# 3. Startup chain (idéntica a Railway)
echo "[DEPLOY] ensure_alembic.py..." | tee -a "$LOG"
python scripts/ensure_alembic.py 2>&1 | tee -a "$LOG"

echo "[DEPLOY] alembic upgrade head..." | tee -a "$LOG"
alembic upgrade head 2>&1 | tee -a "$LOG"

echo "[DEPLOY] verify_schema.py..." | tee -a "$LOG"
python scripts/verify_schema.py 2>&1 | tee -a "$LOG"

# 4. Restart (systemd)
echo "[DEPLOY] Restarting backend..." | tee -a "$LOG"
sudo systemctl restart tesis-backend

# 5. Healthcheck
echo "[DEPLOY] Waiting for healthcheck..." | tee -a "$LOG"
sleep 5
for i in {1..6}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/health || echo "000")
    echo "[DEPLOY] Attempt $i — /health → HTTP $STATUS" | tee -a "$LOG"
    if [ "$STATUS" = "200" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') [DEPLOY] SUCCESS" | tee -a "$LOG"
        exit 0
    fi
    sleep 5
done

echo "$(date '+%Y-%m-%d %H:%M:%S') [DEPLOY] FAILED — healthcheck timeout" | tee -a "$LOG"
exit 1
DEPLOY

chmod +x /var/www/tesis-app/deploy.sh
```

Agregar sudoers para que `tesis` pueda restart sin password:
```bash
echo "tesis ALL=(ALL) NOPASSWD: /bin/systemctl restart tesis-backend" | sudo tee /etc/sudoers.d/tesis-deploy
```

#### 7.4 — Modificar `.github/workflows/deploy.yml`

Reemplazar el job `deploy` (Railway) por SSH deploy:

```yaml
  deploy:
    name: Deploy to VPS
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          port: ${{ secrets.VPS_PORT }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: /var/www/tesis-app/deploy.sh

      - name: Health Check Production
        run: |
          echo "Waiting for deploy to stabilize..."
          sleep 10
          for i in {1..6}; do
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://tu-dominio.com/health" || echo "000")
            echo "Attempt $i — /health → HTTP $STATUS"
            if [ "$STATUS" = "200" ]; then
              echo "Production is up!"
              break
            fi
            [ $i -eq 6 ] && { echo "Health check timeout"; exit 1; }
            sleep 10
          done
```

#### 7.5 — Modificar `.github/workflows/staging.yml`

Misma lógica, pero apuntando al entorno staging (puede ser el mismo VPS con otro puerto o un segundo VPS barato). Si se mantiene un solo servidor, staging y producción comparten VPS pero se despliegan desde branches diferentes.

---

### Fase 8 — Backups automatizados

#### 8.1 — Backup local diario

```bash
sudo mkdir -p /backups/postgres
sudo chown tesis:tesis /backups/postgres

# Cron job: backup diario a las 3 AM
cat > /tmp/pg-backup-cron << 'CRON'
# Backup diario PostgreSQL — LiqExpert
0 3 * * * tesis pg_dump -U app tesis_master | gzip > /backups/postgres/tesis_$(date +\%Y\%m\%d_\%H\%M).sql.gz 2>> /var/log/tesis-backup.log
# Limpiar backups mayores a 30 días
0 4 * * * tesis find /backups/postgres -name "*.sql.gz" -mtime +30 -delete
CRON
sudo crontab -u tesis /tmp/pg-backup-cron
```

#### 8.2 — Sync a almacenamiento externo

Un backup en el mismo disco no protege contra fallo de hardware.
Opciones (elegir una):

**Opción A — rclone a Google Drive / S3:**
```bash
sudo apt install -y rclone
rclone config  # Configurar remote (gdrive, s3, etc.)

# Agregar al cron después del backup:
30 3 * * * tesis rclone copy /backups/postgres remote:tesis-backups/postgres --max-age 7d
```

**Opción B — rsync a segundo servidor:**
```bash
30 3 * * * tesis rsync -avz /backups/postgres/ user@backup-server:/backups/tesis/
```

**Opción C — Mínimo viable: copiar a Object Storage de Hostinger (si incluido en el plan).**

#### 8.3 — Verificar que los backups funcionan

```bash
# Test de restore en una base temporal
sudo -u postgres createdb tesis_test_restore
zcat /backups/postgres/tesis_LATEST.sql.gz | sudo -u postgres psql tesis_test_restore
sudo -u postgres psql tesis_test_restore -c "SELECT count(*) FROM tenants;"
sudo -u postgres dropdb tesis_test_restore
```

---

### Fase 9 — Log rotation

#### 9.1 — Pricing audit log

```bash
sudo tee /etc/logrotate.d/tesis << 'EOF'
/var/www/tesis-app/backend/logs/*.jsonl {
    weekly
    rotate 12
    compress
    missingok
    notifempty
    create 0644 tesis tesis
    copytruncate
}
EOF
```

`copytruncate` evita tener que reiniciar uvicorn — trunca el archivo después de copiar.

#### 9.2 — Deploy log

```bash
sudo tee -a /etc/logrotate.d/tesis << 'EOF'

/var/log/tesis-deploy.log {
    monthly
    rotate 6
    compress
    missingok
    notifempty
    create 0644 tesis tesis
}
EOF
```

---

### Fase 10 — Monitoreo

#### 10.1 — UptimeRobot (gratis)

- URL: `https://tu-dominio.com/health`
- Intervalo: 5 minutos
- Alerta: email/Telegram si HTTP != 200

#### 10.2 — Journald para debugging

```bash
# Ver logs del backend en tiempo real
sudo journalctl -u tesis-backend -f

# Ver últimas 100 líneas
sudo journalctl -u tesis-backend -n 100 --no-pager

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

---

### Fase 11 — CORS y ajustes de código

#### 11.1 — Agregar dominio nuevo a CORS

En `backend/app/main.py`, agregar el dominio a la lista `origins`:

```python
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
    "https://tesis-calculadora-fiscal-staging.up.railway.app",
    "https://tu-dominio.com",       # ← AGREGAR
    "https://www.tu-dominio.com",   # ← AGREGAR
]
```

O mejor: configurar `FRONTEND_URL=https://tu-dominio.com` en `.env` — ya se agrega automáticamente por el bloque existente:

```python
frontend_url = settings.FRONTEND_URL
if frontend_url:
    origins.append(frontend_url)
```

Solo asegurarse de que `FRONTEND_URL` incluya el scheme (`https://`).

---

## 4. Transición y rollback

### Secuencia segura de cutover

```
Día 1-3:  VPS funcionando con copia de la DB. Railway sigue siendo producción.
          Verificar TODO funcione en VPS accediendo por IP directa.

Día 4:    Hacer pg_dump FINAL de Railway (datos más recientes).
          Importar en VPS.
          Cambiar DNS: tu-dominio.com → IP del VPS.
          Railway sigue corriendo como fallback.

Día 5-11: Monitorear VPS como producción principal.
          Railway como fallback (DNS se puede revertir en 5 min).

Día 12:   Si todo funciona: cancelar Railway.
          Si hubo problemas: revertir DNS a Railway.
```

### Rollback instantáneo

- **DNS TTL bajo** (300s = 5 min) durante la migración
- Si algo falla: cambiar el registro A de vuelta a Railway → en 5 min el tráfico regresa
- Mantener Railway activo mínimo 2 semanas post-migración

---

## 5. Checklist pre-migración

```
[ ] VPS provisionado y hardened (firewall, SSH, fail2ban)
[ ] PostgreSQL instalado, usuario creado, listen_addresses = localhost
[ ] Datos importados y verificados (conteo de registros match con Railway)
[ ] Backend arrancando con startup chain completa (ensure_alembic → verify_schema)
[ ] /health retorna 200 con schema ok
[ ] Nginx configurado con todas las locations (/api/v1, /api/v1/ws, /health, /)
[ ] SSL configurado y auto-renew verificado
[ ] WebSocket de auditoría IA funciona (probar en browser)
[ ] CORS incluye el nuevo dominio
[ ] Backups cron configurados y testeados (restore exitoso)
[ ] Backups sincronizados a storage externo
[ ] Log rotation configurado
[ ] CI/CD actualizado: deploy.yml usa SSH en lugar de railway up
[ ] Deploy script funciona end-to-end (git pull → restart → healthcheck)
[ ] UptimeRobot configurado
[ ] DNS con TTL bajo (300s) para rollback rápido
[ ] Railway mantiene activo como fallback durante 2 semanas
```

---

## 6. Comparación de costos (corregida)

| Concepto | Railway (actual) | Hostinger VPS |
|---|---|---|
| Compute | ~$20/mes | $9.99/mes (KVM 4) |
| PostgreSQL | ~$5/mes (plugin) | Incluido (self-managed) |
| Dominio | Subdomain gratis | ~$10/año ($0.83/mes) |
| SSL | Incluido | Gratis (Let's Encrypt) |
| Backups | Automático (incluido) | Self-managed (storage externo $1-3/mes) |
| CI/CD | Railway CLI (incluido) | SSH action (gratis) |
| Monitoreo | Railway dashboard | UptimeRobot gratis + journald |
| **Total** | **~$25-30/mes** | **~$12-14/mes** |
| **Esfuerzo operativo** | Bajo (PaaS) | Alto (self-managed) |

**Trade-off**: ahorramos ~$15/mes pero asumimos la responsabilidad de backups, seguridad, actualizaciones y troubleshooting. Para una tesis doctoral donde el tiempo de investigación es más valioso que $15/mes, evaluar cuidadosamente si el ahorro justifica el esfuerzo.
