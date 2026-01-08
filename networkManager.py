import socket
from udp import broadcast_offer, listen_for_offers
from tcp import create_tcp_server, connect_to_tcp_server, accept_tcp_connection_with_timeout
from pack_manager import pack_request, unpack_request, Card, pack_client_payload, pack_server_payload, unpack_client_payload, unpack_server_payload

'''the purpose of this file is to provide basic connectivity utilities, and be an access point to all smaller network related file
including my udp and tcp files'''
# -------------------------
# Utilities
# -------------------------
def safe_recv(sock: socket.socket, n_bytes: int) -> bytes:
    """Receive exactly n_bytes from socket"""
    data = b""
    while len(data) < n_bytes:
        chunk = sock.recv(n_bytes - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
        data += chunk
    return data
