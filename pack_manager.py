import struct
from typing import Tuple
from my_utils import (
    MAGIC_COOKIE,
    MessageFormat,
    MessageLength,
    MessageType,
    PlayerDecision,
    GameState,
    Card,
    fix_name_length,
    pack_card,
    unpack_card,
)

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