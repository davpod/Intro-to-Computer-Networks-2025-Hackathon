# networkManager.py
import socket
import struct
from typing import Tuple, Optional
from my_utils import *

# -------------------------
# UDP Functions (Server/Client)
# -------------------------

def broadcast_offer(server_name: str, tcp_port: int, interval: float = 1.0):
    """Server: broadcast offer message every `interval` seconds"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_name_bytes = fix_name_length(server_name)

    while True:
        msg = struct.pack(MessageFormat.OFFER.value, MAGIC_COOKIE, MessageType.OFFER.value, tcp_port, server_name_bytes)
        sock.sendto(msg, ('<broadcast>', BROADCAST_UDP_PORT))
        import time
        time.sleep(interval)


def broadcast_offer_once(server_name: str, tcp_port: int):
    """Server: send one UDP offer"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_name_bytes = fix_name_length(server_name)
    msg = struct.pack(MessageFormat.OFFER.value, MAGIC_COOKIE, MessageType.OFFER.value, tcp_port, server_name_bytes)
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
    if timeout:
        sock.settimeout(timeout)

    while True:
        data, addr = sock.recvfrom(1024)
        if len(data) != MessageLength.OFFER.value:
            continue
        magic, msg_type, tcp_port, server_name_bytes = struct.unpack(MessageFormat.OFFER.value, data)
        if magic != MAGIC_COOKIE or msg_type != MessageType.OFFER.value:
            continue
        server_name = server_name_bytes.rstrip(b'\x00').decode()
        server_ip = addr[0]
        return server_ip, tcp_port, server_name

# -------------------------
# TCP Functions
# -------------------------

def create_tcp_server() -> socket.socket:
    """Create TCP server socket, OS picks port"""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', DEFAULT_TCP_PORT))  # 0 = OS picks free port
    server_sock.listen()
    return server_sock


def accept_tcp_connection(server_sock: socket.socket) -> Tuple[socket.socket, str]:
    """Accept new TCP client"""
    client_sock, addr = server_sock.accept()
    return client_sock, addr[0]


def accept_tcp_connection_with_timeout(server_sock: socket.socket, timeout: float = 1.0) -> Tuple[Optional[socket.socket], Optional[str]]:
    """Try to accept a TCP client up to `timeout` seconds"""
    server_sock.settimeout(timeout)
    try:
        return server_sock.accept()
    except socket.timeout:
        return None, None


def connect_to_tcp_server(ip: str, port: int, timeout: float = 5.0) -> socket.socket:
    """Connect to server TCP port"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((ip, port))
    return sock

# -------------------------
# Payload packing/unpacking
# -------------------------

def pack_request(num_rounds: int, client_name: str) -> bytes:
    """Pack TCP request message"""
    client_name_bytes = fix_name_length(client_name)
    return struct.pack(MessageFormat.REQUEST.value, MAGIC_COOKIE, MessageType.REQUEST.value, num_rounds, client_name_bytes)


def unpack_request(data: bytes) -> Tuple[int, str]:
    """Unpack TCP request message"""
    if len(data) != MessageLength.REQUEST.value:
        raise ValueError("Invalid request length")
    magic, msg_type, num_rounds, client_name_bytes = struct.unpack(MessageFormat.REQUEST.value, data)
    if magic != MAGIC_COOKIE or msg_type != MessageType.REQUEST.value:
        raise ValueError("Invalid magic cookie or message type")
    return num_rounds, client_name_bytes.rstrip(b'\x00').decode()


def pack_payload(decision: PlayerDecision = None, round_result: GameState = None, card: Tuple[int, Suits] = None) -> bytes:
    """Pack client or server payload"""
    if decision:
        return struct.pack(MessageFormat.CLIENT_PAYLOAD.value, MAGIC_COOKIE, MessageType.RESPONSE.value, decision.value)
    elif round_result and card:
        rank, suit = card
        card_bytes = pack_card(rank, suit)
        # SERVER_PAYLOAD: magic + type + card_bytes + round_result
        return struct.pack("!IB3sB", MAGIC_COOKIE, MessageType.RESPONSE.value, card_bytes, round_result.value)
    else:
        raise ValueError("Either client decision or server payload required")


def unpack_payload(data: bytes, is_client: bool = True):
    """Unpack payload message"""
    if is_client:
        if len(data) != MessageLength.CLIENT_PAYLOAD.value:
            raise ValueError("Invalid client payload length")
        magic, msg_type, decision_bytes = struct.unpack(MessageFormat.CLIENT_PAYLOAD.value, data)
        if magic != MAGIC_COOKIE or msg_type != MessageType.RESPONSE.value:
            raise ValueError("Invalid payload")
        return PlayerDecision(decision_bytes)
    else:
        if len(data) != MessageLength.SERVER_PAYLOAD.value:
            raise ValueError("Invalid server payload length")
        # Unpack server payload: card + round result
        magic, msg_type, card_bytes, round_result = struct.unpack(MessageFormat.SERVER_PAYLOAD.value, data)
        if magic != MAGIC_COOKIE or msg_type != MessageType.RESPONSE.value:
            raise ValueError("Invalid payload")
        rank, suit = unpack_card(card_bytes)
        return (rank, Suits(suit)), GameState(round_result)

# -------------------------
# Utilities
# -------------------------

def safe_recv(sock: socket.socket, n_bytes: int) -> bytes:
    """Receive exactly n_bytes from socket"""
    data = b""
    while len(data) < n_bytes:
        packet = sock.recv(n_bytes - len(data))
        if not packet:
            raise ConnectionError("Socket closed during recv")
        data += packet
    return data
