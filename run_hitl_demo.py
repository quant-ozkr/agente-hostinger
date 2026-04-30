import os
import sys

# Asegurar que el path está configurado
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.agent_graph import create_tech_agent_graph

def run_demo():
    print("Iniciando demostración HITL (Human-in-the-loop) del Cerebro Técnico...")
    
    # Instanciar el grafo
    graph = create_tech_agent_graph()
    
    # Thread ID para mantener la sesión
    config = {"configurable": {"thread_id": "demo-hitl-1"}}
    
    # Estado inicial forzando un problema de base de datos para disparar HITL
    initial_state = {
        "messages": [],
        "vps_metrics": "Error en PostgreSQL: Database corruption detected",
        "issues_found": [],
        "actions_taken": [],
        "requires_human": False
    }
    
    print("\n--- Ejecución Inicial ---")
    # Stream events until interruption
    for event in graph.stream(initial_state, config=config):
        for k, v in event.items():
            print(f"Sub-agente [{k}] terminó su tarea.")
            if "issues_found" in v:
                print(f"   => Problemas detectados: {v['issues_found']}")
            if "actions_taken" in v:
                print(f"   => Acciones tomadas: {v['actions_taken']}")
                
    # Comprobar si el grafo se detuvo
    snapshot = graph.get_state(config)
    
    if snapshot.next:
        print(f"\n[ALERTA] El grafo se ha detenido antes del nodo: {snapshot.next}")
        print("Se requiere aprobación humana para proceder.")
        
        # Interacción humana
        respuesta = input("¿Aprobar acción correctiva de base de datos? (s/n): ")
        
        if respuesta.lower() == 's':
            print("\nContinuando ejecución...")
            # Actualizamos el estado o simplemente reanudamos
            # En LangGraph v0.2+ podemos usar Command(resume=...) o invocar con None
            for event in graph.stream(None, config=config):
                for k, v in event.items():
                    print(f"Sub-agente [{k}] terminó su tarea.")
        else:
            print("\nAcción denegada por el usuario. Abortando.")
            # Podemos actualizar el estado manualmente para indicar rechazo
            graph.update_state(config, {"actions_taken": ["Acción denegada por humano"]})
    else:
        print("\nEl grafo finalizó sin requerir intervención humana.")

if __name__ == "__main__":
    run_demo()
