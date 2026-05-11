from graph.agent_graph import create_tech_agent_graph

def test_graph_compilation():
    """Verifica que el grafo compile correctamente."""
    graph = create_tech_agent_graph()
    assert graph is not None

def test_graph_flow_no_issues():
    """Prueba que si no hay incidentes, el flujo pase de monitor a auditor a fin."""
    graph = create_tech_agent_graph()
    
    initial_state = {
        "messages": [],
        "vps_metrics": "CPU: 10%, RAM: 2GB",
        "issues_found": [],
        "actions_taken": [],
        "requires_human": False
    }
    
    # Run the graph
    result = graph.invoke(initial_state, {"configurable": {"thread_id": "test_1"}})
    
    # Verificamos que no se detectaron problemas y llegó a auditor o terminó
    assert not result["requires_human"]
    assert result["issues_found"] == []
