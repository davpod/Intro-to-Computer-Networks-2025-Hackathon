# networkManager.py
import socket
import struct
from typing import Tuple, Optional
from my_utils import (
    MAGIC_COOKIE,
    BROADCAST_UDP_PORT,
    DEFAULT_TCP_PORT,
    MessageFormat,
    MessageLength,
    MessageType,
    PlayerDecision,
    GameState,
    Suits,
    Card,
    fix_name_length,
    pack_card,
    unpack_card,
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


# -------------------------
# Payload packing/unpacking
# -------------------------

def pack_request(num_rounds: int, client_name: str) -> bytes:
    """Pack TCP request message"""
    return struct.pack(
        MessageFormat.REQUEST.value,
        MAGIC_COOKIE,
        MessageType.REQUEST.value,
        num_rounds,
        fix_name_length(client_name),
    )


def unpack_request(data: bytes) -> Tuple[int, str]:
    """Unpack TCP request message"""
    if len(data) != MessageLength.REQUEST.value:
        raise ValueError("Invalid request length")

    magic, msg_type, num_rounds, client_name_bytes = struct.unpack(
        MessageFormat.REQUEST.value, data
    )

    if magic != MAGIC_COOKIE or msg_type != MessageType.REQUEST.value:
        raise ValueError("Invalid request message")

    return num_rounds, client_name_bytes.rstrip(b'\x00').decode()


def pack_client_payload(decision: PlayerDecision) -> bytes:
    """Pack client decision payload"""
    return struct.pack(
        MessageFormat.CLIENT_PAYLOAD.value,
        MAGIC_COOKIE,
        MessageType.RESPONSE.value,
        decision.value,
    )


def pack_server_payload(card: Card, state: GameState) -> bytes:
    """Pack server payload with a card and round state"""
    card_bytes = pack_card(card.rank, card.suit.value)
    return struct.pack(
        MessageFormat.SERVER_PAYLOAD.value,
        MAGIC_COOKIE,
        MessageType.RESPONSE.value,
        card_bytes,
        state.value,
    )


def unpack_client_payload(data: bytes) -> PlayerDecision:
    """Unpack client decision"""
    if len(data) != MessageLength.CLIENT_PAYLOAD.value:
        raise ValueError("Invalid client payload length")

    magic, msg_type, decision_bytes = struct.unpack(
        MessageFormat.CLIENT_PAYLOAD.value, data
    )

    if magic != MAGIC_COOKIE or msg_type != MessageType.RESPONSE.value:
        raise ValueError("Invalid client payload")

    return PlayerDecision(decision_bytes)


def unpack_server_payload(data: bytes) -> Tuple[Card, GameState]:
    """Unpack server payload"""
    if len(data) != MessageLength.SERVER_PAYLOAD.value:
        raise ValueError("Invalid server payload length")

    magic, msg_type, card_bytes, state = struct.unpack(
        MessageFormat.SERVER_PAYLOAD.value, data
    )

    if magic != MAGIC_COOKIE or msg_type != MessageType.RESPONSE.value:
        raise ValueError("Invalid server payload")

    card = unpack_card(card_bytes)
    return card, GameState(state)


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
