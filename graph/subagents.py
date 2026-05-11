import logging
from typing import TypedDict, Annotated, Sequence, List
import operator
from langchain_core.messages import BaseMessage

logger = logging.getLogger("subagents")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    vps_metrics: str
    issues_found: List[str]
    actions_taken: List[str]
    requires_human: bool

def monitor_agent(state: AgentState) -> AgentState:
    """Sub-agente que lee las métricas del VPS y busca anomalías."""
    # Aquí iría la lógica LLM para interpretar las métricas. 
    # Por ahora lo simulamos:
    logger.info("Monitor Agent evaluando métricas...")
    
    issues = []
    # Simulación de evaluación
    if "100%" in state.get("vps_metrics", ""):
        issues.append("Uso de CPU al 100%")
    if "corruption" in state.get("vps_metrics", "").lower():
        issues.append("Database corruption detected")
        
    return {"issues_found": issues}

def healer_agent(state: AgentState) -> AgentState:
    """Sub-agente que toma decisiones correctivas en base a los issues."""
    logger.info("Healer Agent analizando issues...")
    actions = []
    requires_human = state.get("requires_human", False)
    
    for issue in state.get("issues_found", []):
        if "CPU" in issue:
            actions.append("Reiniciando servicios no críticos para liberar CPU")
        elif "Database" in issue:
            actions.append("Se requiere intervención humana para corrupción de base de datos")
            requires_human = True
            
    return {"actions_taken": actions, "requires_human": requires_human}

def auditor_agent(state: AgentState) -> AgentState:
    """Sub-agente que verifica la seguridad y logs de auditoría."""
    logger.info("Auditor Agent revisando logs de seguridad...")
    actions = []
    if not state.get("issues_found"):
        actions.append("No se detectaron brechas de seguridad")
    return {"actions_taken": actions}
