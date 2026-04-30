import os
import sqlite3
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Importar sub-agentes
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
    # En producción real, este nodo sirve de punto de interrupción
    # usando interrupt_on=["human_approval"]
    return state

def create_tech_agent_graph():
    """Compila y retorna el grafo del Cerebro Técnico con persistencia SQLite."""
    builder = StateGraph(AgentState)
    
    # Añadir nodos
    builder.add_node("monitor", monitor_agent)
    builder.add_node("healer", healer_agent)
    builder.add_node("auditor", auditor_agent)
    builder.add_node("human_approval", human_approval)
    
    # Definir flujo
    builder.add_edge(START, "monitor")
    builder.add_conditional_edges("monitor", router)
    
    # El healer puede requerir intervención humana, usamos un router secundario o el mismo
    def healer_router(state: AgentState) -> str:
        if state.get("requires_human"):
            return "human_approval"
        return "auditor"
        
    builder.add_conditional_edges("healer", healer_router)
    builder.add_edge("human_approval", END)
    builder.add_edge("auditor", END)
    
    # Configurar persistencia (SQLite local para funcionar sin depender del VPS)
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tech_agent_checkpoints.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Checkpointer
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    
    # Compilar el grafo indicando que se detenga antes de human_approval
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["human_approval"]
    )
    
    return graph

if __name__ == "__main__":
    # Test simple del grafo
    graph = create_tech_agent_graph()
    
    initial_state = {
        "messages": [],
        "vps_metrics": "CPU at 100%, RAM at 80%",
        "issues_found": [],
        "actions_taken": [],
        "requires_human": False
    }
    
    config = {"configurable": {"thread_id": "tech-agent-test-1"}}
    
    print("Ejecutando grafo...")
    for event in graph.stream(initial_state, config=config):
        for k, v in event.items():
            print(f"[{k}] -> {v}")
