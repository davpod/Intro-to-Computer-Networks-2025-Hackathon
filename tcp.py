import socket
from typing import Tuple, Optional
from my_utils import DEFAULT_TCP_PORT

# -------------------------
# TCP Functions
# -------------------------

def create_tcp_server() -> socket.socket:
    """Create TCP server socket, OS picks port"""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', DEFAULT_TCP_PORT))  # 0 = OS picks free port
    server_sock.listen()
    return server_sock


def accept_tcp_connection_with_timeout(
    server_sock: socket.socket,
    timeout: float
) -> Tuple[Optional[socket.socket], Optional[str]]:
    """Accept TCP client with timeout"""
    server_sock.settimeout(timeout)
    try:
        client_sock, addr = server_sock.accept()
        return client_sock, addr[0]
    except socket.timeout:
        return None, None


def connect_to_tcp_server(ip: str, port: int, timeout: float = 5.0) -> socket.socket:
    """Connect to server TCP socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((ip, port))
    return sock