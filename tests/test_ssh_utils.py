from unittest.mock import patch
from core.ssh_utils import SSHConnection

def test_ssh_connection_reject_policy():
    """Verifica que SSHConnection siempre aplica RejectPolicy y no AutoAddPolicy."""
    with patch("core.ssh_utils.paramiko.SSHClient") as MockClient:
        mock_client_instance = MockClient.return_value
        
        # Al inicializar no debería explotar si los args son validos
        conn = SSHConnection(ip="127.0.0.1", username="test", key_path="/fake/path")
        
        # Validar que set_missing_host_key_policy fue llamado con RejectPolicy
        from paramiko import RejectPolicy
        mock_client_instance.set_missing_host_key_policy.assert_called_once()
        
        # Extraemos el argumento posicional que se le pasó
        args, kwargs = mock_client_instance.set_missing_host_key_policy.call_args
        assert isinstance(args[0], RejectPolicy), "Debe usar RejectPolicy para prevenir MITM"
