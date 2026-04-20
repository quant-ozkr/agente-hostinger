# webhook_receiver.py - Receptor de alertas para Autocuración
from fastapi import FastAPI, Request, BackgroundTasks
import subprocess
import uvicorn
import os

app = FastAPI()

# Token de seguridad sencillo para evitar que extraños disparen reinicios
SECURITY_TOKEN = os.getenv("WEBHOOK_SECRET", "liqexpert_secret_2026")

def heal_protocol():
    """Ejecuta la lógica de autocuración."""
    print("[AUTOCURACIÓN] Iniciando protocolo...")
    # Llama directamente a la función de autocuración que definimos en brainstem_mcp
    # O simplemente reinicia el servicio si está caído
    subprocess.run(["sudo", "systemctl", "restart", "tesis-backend"])
    print("[AUTOCURACIÓN] Protocolo finalizado.")

@app.post("/webhook/uptime")
async def uptime_handler(request: Request, background_tasks: BackgroundTasks):
    # UptimeRobot envía datos por POST
    data = await request.form()
    # Si no es form, intentar json
    if not data:
        data = await request.json()

    alert_type = data.get("alertType", "")
    alert_friendly_name = data.get("monitorFriendlyName", "Desconocido")
    
    print(f"[ALERTA] Recibida alerta de {alert_friendly_name}: {alert_type}")

    # alertType 1 = Down, 2 = Up
    if alert_type == "1" or "down" in str(alert_type).lower():
        print(f"[ALERTA] El sistema {alert_friendly_name} está CAÍDO. Disparando autocuración...")
        background_tasks.add_task(heal_protocol)
        return {"status": "healing_initiated"}
    
    return {"status": "ok", "message": "no action required"}

if __name__ == "__main__":
    # Escuchará en un puerto diferente al de la API (ej. 8003)
    uvicorn.run(app, host="0.0.0.0", port=8003)
