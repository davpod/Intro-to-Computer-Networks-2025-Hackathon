import socket
import struct
from typing import Tuple, Optional
from my_utils import (
    MAGIC_COOKIE,
    BROADCAST_UDP_PORT,
    MessageFormat,
    MessageLength,
    MessageType,
    fix_name_length,
)
# -------------------------
# UDP Functions (Server/Client)
# -------------------------
def broadcast_offer(server_name: str, tcp_port: int):
    """Server: send one UDP offer"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    server_name_bytes = fix_name_length(server_name)
    msg = struct.pack(
        MessageFormat.OFFER.value,
        MAGIC_COOKIE,
        MessageType.OFFER.value,
        tcp_port,
        server_name_bytes
    )
    sock.sendto(msg, ('<broadcast>', BROADCAST_UDP_PORT))
    sock.close()


def listen_for_offers(timeout: Optional[float] = None) -> Tuple[str, int, str]:
    """Client: listen for UDP offer, return (server_ip, tcp_port, server_name)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    else:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', BROADCAST_UDP_PORT))
    if timeout is not None:
        sock.settimeout(timeout)

    while True:
        data, addr = sock.recvfrom(1024)

        if len(data) != MessageLength.OFFER.value:
            continue

        magic, msg_type, tcp_port, server_name_bytes = struct.unpack(
            MessageFormat.OFFER.value, data
        )

        if magic != MAGIC_COOKIE or msg_type != MessageType.OFFER.value:
            continue

        server_name = server_name_bytes.rstrip(b'\x00').decode()
        return addr[0], tcp_port, server_name




