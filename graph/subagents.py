import logging
from typing import TypedDict, Annotated, Sequence, List
import operator
from langchain_core.messages import BaseMessage, AIMessage

# Importar habilidades (skills)
from skills.cicd.health_check import health_check
from skills.cicd.build_and_deploy import build_and_deploy
from skills.monitoring.notify_orchestrator import notify_orchestrator
from skills.maintenance.sync_db_params import sync_db_params

logger = logging.getLogger("subagents")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    vps_metrics: str
    issues_found: List[str]
    actions_taken: List[str]
    requires_human: bool

def monitor_agent(state: AgentState) -> AgentState:
    """Sub-agente que usa la skill de health_check para evaluar el sistema."""
    logger.info("Monitor Agent iniciando verificación de salud v2.0...")
    
    # Ejecutar la skill determinista
    health_results = health_check()
    
    issues = []
    if "❌" in health_results:
        issues.append(f"Fallo de salud detectado: {health_results}")
        
    # El LLM puede ver el resultado en los mensajes
    return {
        "messages": [AIMessage(content=f"Resultado del Health Check:\n{health_results}")],
        "issues_found": issues
    }

def healer_agent(state: AgentState) -> AgentState:
    """Sub-agente que toma acciones correctivas."""
    logger.info("Healer Agent analizando issues...")
    actions = []
    requires_human = state.get("requires_human", False)
    
    for issue in state.get("issues_found", []):
        if "UNREACHABLE" in issue or "FAILED" in issue:
            # Intentar autocuración vía redeploy (build_and_deploy)
            msg = "Intentando autocuración reiniciando servicios..."
            notify_orchestrator(f"🛠 {msg}")
            deploy_result = build_and_deploy()
            actions.append(f"Redeploy ejecutado: {deploy_result[:100]}")
        
        if "Critical" in issue:
            requires_human = True
            
    return {"actions_taken": actions, "requires_human": requires_human}

def auditor_agent(state: AgentState) -> AgentState:
    """Sub-agente de auditoría y notificaciones finales."""
    logger.info("Auditor Agent finalizando ciclo...")
    
    summary = "Ciclo de mantenimiento completado."
    if state.get("actions_taken"):
        summary += f" Acciones: {', '.join(state['actions_taken'])}"
    
    # Notificar al Orchestrator el fin del ciclo si hubo cambios
    if state.get("issues_found"):
        notify_orchestrator(f"📋 Resumen de Infraestructura: {summary}")
        
    return {
        "messages": [AIMessage(content=summary)]
    }
