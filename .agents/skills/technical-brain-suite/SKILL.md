---
name: technical-brain-suite
description: Habilidad maestra para el monitoreo, despliegue y estabilización de la infraestructura multi-agente LiqExpert. Activa esta habilidad ante fallos de CI/CD, bloqueos de gobernanza o problemas de conectividad inter-cerebro.
compatibility: Python 3.10+, paramiko, requests, GitHub Personal Access Token (GITHUB_TOKEN).
metadata:
  version: "1.0"
  author: "Antigravity Technical Brain"
  domain: "DevOps & Ecosistema Multi-Agente"
---

# Technical Brain Suite (LiqExpert)

Esta suite proporciona las herramientas y el conocimiento necesario para mantener la estabilidad del ecosistema multi-agente distribuido entre GitHub y el VPS de Hostinger.

## 🏗️ Arquitectura del Ecosistema
- **Repositorio Fiscal**: `quant-ozkr/tesis-calculadora-fiscal` (Puerto 8008 - MCP).
- **Repositorio Marketing**: `quant-ozkr/agencia-mkt-aut` (Puerto 8001 - Backend).
- **Repositorio Hostinger**: `quant-ozkr/agente-hostinger` (Puerto 8000 - Brainstem).

## 🛠️ Herramientas Disponibles

### 1. Monitoreo Global (`scripts/monitor.py`)
Úsala para obtener una visión 360° del estado de los 3 repositorios, sus ramas Main/Staging y el estado de sus servicios en el VPS.
- **Cuándo usar**: Siempre que el usuario pregunte "¿Cómo va todo?" o "Verifica el estado".

### 2. Gestor de Despliegues SSH (`scripts/deploy_fixer.sh`)
Script robusto para despliegues manuales o automáticos.
- **Características**: Usa rutas absolutas (`readlink`), maneja compilaciones directas de Vite y reinicia los servicios correctos según el path.
- **Ubicación en VPS**: `/var/www/tesis-app/deploy.sh` y `/var/www/tesis-staging/deploy.sh`.

### 3. Cumplimiento ISO27001 (`scripts/compliance.py`)
Generador de evidencias de seguridad (`SAR`) y planes de ejecución (`ExecPlan`).
- **Cuándo usar**: Cuando el CI/CD falle en el paso `Security Auditor Review Gate` debido a cambios masivos.
- **Regla**: Solo generar evidencia si se ha verificado manualmente la integridad del código (ej. linting aprobado).

## 🚨 Protocolo de Resolución de Fallos

### A. Fallo en el "Deploy via SSH"
1. Verificar permisos de la carpeta de destino (`www-data` para servicios, `tesis` para git).
2. Asegurar que `deploy.sh` tenga el bit de ejecución (`chmod +x`).
3. Revisar si el fallo es por `dist/` inexistente (usar el nuevo script robusto).

### B. Fallo de "ChromaDB ReadOnly"
- **Causa**: El servicio corre como `www-data` pero la carpeta `data/chroma_db` pertenece al usuario de SSH.
- **Solución**: `sudo chown -R www-data:www-data /var/www/tesis-app/backend/data/chroma_db`.

### C. Fallo en "Governance/Security Gate"
- **Acción**: Crear `ExecPlan` en `.agent/execplans/` y evidencia SAR en `.compliance/evidence/security-reviews/`. Actualizar `audit_log.json`.

## 📌 Mejores Prácticas del Protocolo
- **Sincronización**: Antes de dar por terminada una tarea en `main`, sincroniza con `staging` para evitar "deriva de configuración".
- **Logs**: Usar siempre `journalctl -u <servicio> -n 50` para diagnósticos profundos.
- **Health Checks**: No basta con que el servicio esté `active`, debe responder `{"status":"healthy"}` en su respectivo puerto.
