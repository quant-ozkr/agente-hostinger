import os
import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Importar sub-agentes y estado
from graph.subagents import AgentState, monitor_agent, healer_agent, auditor_agent

def router(state: AgentState) -> str:
    """Decide qué sub-agente ejecutar basado en el estado."""
    if state.get("requires_human"):
        return "human_approval"
    if state.get("issues_found"):
        return "healer"
    return "auditor"

def human_approval(state: AgentState) -> AgentState:
    """Nodo para interrupción humana."""
    # Este nodo sirve de punto de interrupción
    return state

def build_infrastructure_graph():
    """Compila y retorna el grafo de gestión de infraestructura v2.0."""
    builder = StateGraph(AgentState)
    
    # Añadir nodos
    builder.add_node("monitor", monitor_agent)
    builder.add_node("healer", healer_agent)
    builder.add_node("auditor", auditor_agent)
    builder.add_node("human_approval", human_approval)
    
    # Definir flujo
    builder.add_edge(START, "monitor")
    builder.add_conditional_edges("monitor", router)
    
    def healer_router(state: AgentState) -> str:
        if state.get("requires_human"):
            return "human_approval"
        return "auditor"
        
    builder.add_conditional_edges("healer", healer_router)
    builder.add_edge("human_approval", END)
    builder.add_edge("auditor", END)
    
    # Persistencia local
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tech_agent_checkpoints.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["human_approval"]
    )
    
    return graph

# Alias para compatibilidad
create_tech_agent_graph = build_infrastructure_graph
