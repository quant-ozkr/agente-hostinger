# 🛠️ VPS Troubleshooting & Optimization Guide

Este documento consolida las lecciones aprendidas durante la gestión y mantenimiento del VPS de LiqExpert.

## 🔑 Conectividad SSH
- **Formato de Llave:** Paramiko (usado por el agente) prefiere llaves en formato OpenSSH. Si usas llaves RSA antiguas, asegúrate de cargarlas explícitamente o convertirlas.
- **Permisos en Windows:** Para que el cliente SSH de Windows use una llave, debe tener permisos restrictivos (`icacls .ssh_temp/id_rsa /inheritance:r /grant:r "$($env:USERNAME):R"`).
- **Fin de Línea (LF):** Las llaves privadas copiadas desde entornos Windows pueden tener `CRLF`. Siempre convertir a `LF` antes de usarlas en el VPS.
- **Fallback de Password:** Si la llave falla por configuración del servidor, usar autenticación por contraseña como respaldo seguro (nunca loguear la contraseña).

## 🗄️ Base de Datos (PostgreSQL)
- **Migraciones Fallidas:** Si el backend falla al iniciar tras un deploy, verifica columnas faltantes con `\d tabla`. A veces Alembic requiere intervención manual si hubo cambios concurrentes.
- **Sincronización de Parámetros:**
    - Usar `pg_dump --data-only --column-inserts` para exportar solo datos.
    - **Encoding:** Forzar exportación a `UTF-8` sin BOM para evitar errores de secuencia de bytes (`0xff`).
    - **Integridad:** Eliminar IDs de usuarios locales (`updated_by`) con `sed` o scripts de Python antes de importar para evitar errores de llave foránea.
    - **Limpieza:** Usar `TRUNCATE TABLE ... CASCADE` antes de importar para asegurar una sincronización limpia.

## 🌐 Nginx y Frontend
- **Configuración de Proxy:** Las rutas de agentes deben terminar en `/` en el `proxy_pass` (ej: `proxy_pass http://127.0.0.1:8002/;`) para que la sub-ruta sea removida correctamente.
- **CORS:** El frontend requiere cabeceras CORS explícitas en Nginx para comunicación entre contenedores (especialmente para métodos `OPTIONS`).
- **Build de Vite:** Siempre crear un archivo `.env.production` en la carpeta del frontend antes de ejecutar `npm run build`. Vite inyecta estas variables *en tiempo de compilación*.
- **Ruta de Despliegue:** Nginx suele apuntar a `backend/static`. Asegúrate de que `outDir` en `vite.config.js` o el comando `cp` coincidan con esta ruta.

## 🧠 Modelos de IA (LLM)
- **Errores 429 (Resource Exhausted):** Común en niveles gratuitos de Gemini.
- **Estrategia de Respaldo:**
    1.  Configurar **Groq (Llama 3.3 70B)** como motor principal para alta velocidad y cuotas generosas.
    2.  Usar **Gemini** como fallback.
- **Variables de Entorno:** Asegurar que `LLM_MODEL`, `AGENT_MODEL` y `SUPERVISOR_MODEL` estén sincronizados en todos los archivos `.env` (raíz y subdirectorios de agentes).
- **Recursion Limit:** Aumentar el `recursion_limit` en `deepagents.toml` para permitir que el agente reintente llamadas tras fallos de cuota.
