import os
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("heartbeat")

# Importar el grafo
from graph.agent_graph import create_tech_agent_graph

app = FastAPI(title="Tech Agent Heartbeat Listener")
graph = create_tech_agent_graph()

class HeartbeatPayload(BaseModel):
    source: str
    event_type: str
    message: str
    severity: str = "info"

def invoke_agent_async(payload: HeartbeatPayload):
    """Invoca al agente LangGraph en background."""
    logger.info(f"Despertando al Cerebro Técnico por evento de {payload.source}...")
    
    # Preparamos el estado inicial para el agente
    initial_state = {
        "messages": [],
        "vps_metrics": f"Alerta desde {payload.source}: {payload.message}",
        "issues_found": [payload.message] if payload.severity in ["warning", "error", "critical"] else [],
        "actions_taken": [],
        "requires_human": payload.severity == "critical"
    }
    
    # Usamos un thread_id basado en la fuente y el tipo para agrupar en el checkpointer
    thread_id = f"tech-agent:{payload.source}:{payload.event_type}"
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Invocamos el grafo
        final_state = graph.invoke(initial_state, config=config)
        logger.info(f"Agente finalizó. Acciones tomadas: {final_state.get('actions_taken', [])}")
        
        # Si requiere humano (llegó al nodo human_approval)
        if final_state.get("requires_human"):
            logger.warning(f"¡Atención! El caso en {thread_id} requiere aprobación humana.")
            
    except Exception as e:
        logger.error(f"Error ejecutando el agente: {e}")

@app.post("/heartbeat")
async def receive_heartbeat(payload: HeartbeatPayload, background_tasks: BackgroundTasks):
    """Endpoint para recibir señales del VPS (ej. systemd on-failure)."""
    
    # Validar fuente mínima (en producción debería usar tokens)
    if not payload.source:
        raise HTTPException(status_code=400, detail="Missing source")
        
    logger.info(f"Heartbeat recibido: [{payload.severity}] {payload.event_type} - {payload.message}")
    
    # Enviar al agente en background para no bloquear la respuesta
    background_tasks.add_task(invoke_agent_async, payload)
    
    return {"status": "accepted", "message": "Heartbeat encolado para el Cerebro Técnico"}

if __name__ == "__main__":
    logger.info("Iniciando Heartbeat Listener en puerto 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8006)
