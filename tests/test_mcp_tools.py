import pytest
from unittest.mock import patch
from brainstem_mcp import restart_service, resolver_bloqueo_puerto

@patch("brainstem_mcp.subprocess.run")
def test_restart_service_valid(mock_run):
    """Prueba que los servicios permitidos se reinicien."""
    # Configurar el mock
    mock_run.return_value.stdout = "Restarted"
    mock_run.return_value.returncode = 0
    
    result = restart_service("tesis-backend")
    assert "Restarted" in result
    mock_run.assert_called_once()
    assert "sudo systemctl restart tesis-backend" in mock_run.call_args[0][0]

@patch("brainstem_mcp.subprocess.run")
def test_restart_service_invalid(mock_run):
    """Prueba que intente inyección o servicios no permitidos se rechacen."""
    result = restart_service("rm -rf /")
    assert "Servicio no autorizado" in result
    mock_run.assert_not_called()

@patch("brainstem_mcp.subprocess.run")
def test_resolver_bloqueo_puerto_invalid_type(mock_run):
    """Prueba mitigación de inyección en puerto."""
    result = resolver_bloqueo_puerto("8001; rm -rf /")
    assert "Puerto inválido" in result
    mock_run.assert_not_called()
