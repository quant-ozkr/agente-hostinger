# webhook_receiver.py - Receptor de alertas para Autocuración y Despliegue
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Header
import subprocess
import uvicorn
import os
import logging

import httpx
from skills.cicd.build_and_deploy import build_and_deploy

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webhook-receiver")

app = FastAPI()

# Direcciones de la Trinidad Agéntica en el VPS
BRAINS = {
    "logico": "http://127.0.0.1:8001/health",
    "social_app": "http://127.0.0.1:8002/",
    "social_mcp": "http://127.0.0.1:8005/health",
    "tecnico": "http://127.0.0.1:8004/health"
}

# Token de seguridad sencillo para evitar que extraños disparen reinicios/deploys
# Se recomienda configurar esto en el .env del VPS
SECURITY_TOKEN = os.getenv("WEBHOOK_SECRET", "liqexpert_secret_2026")

@app.get("/trinidad/status")
async def get_trinidad_status():
    """Diagnóstico de la comunicación bidireccional entre cerebros."""
    results = {}
    async with httpx.AsyncClient(timeout=2.0) as client:
        for name, url in BRAINS.items():
            try:
                resp = await client.get(url)
                results[name] = {"status": "online", "code": resp.status_code}
            except Exception as e:
                results[name] = {"status": "offline", "error": str(e)}

    return {
        "status": "connected" if all(r["status"] == "online" for r in results.values()) else "degraded",
        "brains": results
    }

def heal_protocol():
    """Ejecuta la lógica de autocuración."""
    logger.info("[AUTOCURACIÓN] Iniciando protocolo...")
    # Intenta reiniciar el servicio del cerebro técnico que es el que corre el orquestador/mcp
    subprocess.run(["sudo", "systemctl", "restart", "cfo-brainstem"])
    logger.info("[AUTOCURACIÓN] Protocolo finalizado.")

def deploy_protocol():
    """Ejecuta el despliegue optimizado."""
    logger.info("[DEPLOY] Iniciando despliegue desde webhook...")
    result = build_and_deploy()
    logger.info(f"[DEPLOY] Resultado: {result}")

@app.post("/webhook/uptime")
async def uptime_handler(request: Request, background_tasks: BackgroundTasks):
    """Manejador para UptimeRobot."""
    # UptimeRobot envía datos por POST
    try:
        data = await request.form()
        if not data:
            data = await request.json()
    except Exception:
        return {"status": "error", "message": "invalid data format"}

    alert_type = data.get("alertType", "")
    alert_friendly_name = data.get("monitorFriendlyName", "Desconocido")
    
    logger.info(f"[ALERTA] Recibida alerta de {alert_friendly_name}: {alert_type}")

    # alertType 1 = Down, 2 = Up
    if alert_type == "1" or "down" in str(alert_type).lower():
        logger.info(f"[ALERTA] El sistema {alert_friendly_name} está CAÍDO. Disparando autocuración...")
        background_tasks.add_task(heal_protocol)
        return {"status": "healing_initiated"}
    
    return {"status": "ok", "message": "no action required"}

@app.post("/webhook/deploy")
async def deploy_handler(request: Request, background_tasks: BackgroundTasks, x_webhook_secret: str = Header(None)):
    """
    Endpoint para disparar despliegue desde GitHub Actions.
    Requiere el header X-Webhook-Secret.
    """
    if not x_webhook_secret or x_webhook_secret != SECURITY_TOKEN:
        logger.warning(f"[DEPLOY] Intento de acceso no autorizado desde {request.client.host}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info("[DEPLOY] Petición de despliegue recibida correctamente.")
    background_tasks.add_task(deploy_protocol)
    
    return {"status": "deploy_initiated", "message": "Pulling latest images and updating containers..."}

if __name__ == "__main__":
    # Escuchará en un puerto diferente al de la API (8006)
    uvicorn.run(app, host="0.0.0.0", port=8006)
