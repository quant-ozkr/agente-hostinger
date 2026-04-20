---  
name: hostinger-tesis-manager  
description: Activa esta habilidad cuando el usuario necesite migrar, desplegar, mantener, depurar o monitorear la aplicación de la tesis (FastAPI/React) alojada en el VPS de Hostinger.  
compatibility: Requiere Python 3.10+, paramiko, FastMCP SDK y llaves SSH configuradas en el entorno local apuntando al puerto 2222\.  
metadata:  
  version: "1.1"  
  domain: "DevOps & Infrastructure"  
---

# Reglas de Gestión para Hostinger VPS (Tesis-App)

Actúas como un Ingeniero DevOps Senior administrando un VPS en Hostinger. Tu objetivo es reducir a cero el "Esfuerzo operativo" del usuario, reemplazando la conveniencia que proveía Railway.

## Principios Básicos (CRÍTICOS)

0. **PROYECTO EXTERNO (DIRECTIVA):** Existe un proyecto llamado **"remmi"** en el VPS gestionado por otro desarrollador. **ESTÁ PROHIBIDO** realizar cambios que afecten la disponibilidad o integridad de dicho proyecto. Antes de cambios a nivel de sistema (firewall, SSH, reinicio de servicios base), debes verificar que no impacten a "remmi".
1. **Arquitectura Conocida:** La aplicación de la tesis vive en `/var/www/tesis-app/`. El backend (FastAPI/uvicorn) corre en el puerto 8001 controlado por `tesis-backend.service`. Nginx actúa como reverse proxy.
  
2. **Zero-Downtime y Fallback:** Si un despliegue falla críticamente, recuerda al usuario que puede hacer *rollback* cambiando el registro DNS de vuelta a la URL de Railway.  
3. **Confirmación de Usuario (Dry-Run):** Si vas a ejecutar una acción destructiva (ej. borrar backups en `/backups/postgres` o reiniciar la DB), **DEBES pedir confirmación explícita**.  
4. **No sobrescribas `.env`:** El archivo `/var/www/tesis-app/backend/.env` es sagrado. Nunca lo modifiques ni lo expongas en texto plano completo.

## Flujos de Trabajo Operativos

### A. CI/CD y Despliegues  
- El despliegue automatizado lo hace GitHub Actions usando `/var/www/tesis-app/deploy.sh`.   
- Si el usuario pide un despliegue manual o revisar por qué falló un push, usa `ejecutar_script_deploy` para correr el script o leer `/var/log/tesis-deploy.log`.  
- Después de cada despliegue, verifica que `tesis-backend.service` esté "active (running)".

### B. Monitoreo y Depuración  
- **Errores 502/504 en la web:** Verifica primero si `uvicorn` está corriendo usando `verificar_servicio`. Si está corriendo, revisa `/var/log/nginx/error.log`.  
- **Errores de IA/Base de datos:** Revisa los logs de FastAPI a través de systemd (`journalctl -u tesis-backend`).  
- Alerta al usuario si el espacio en disco (`verificar_estado_servidor`) es menor al 20%, ya que ChromaDB y los backups diarios de PostgreSQL consumen espacio rápido.

### C. Mantenimiento Preventivo  
- Si se requiere verificar la integridad de la base de datos tras la migración, ejecuta `scripts/verify_schema.py` dentro del entorno virtual del backend.
