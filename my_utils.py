from enum import Enum
import struct
#this file is for shared utils and constants, and is the place for all hardcoded variables that will be used by both client and server
MAGIC_COOKIE = 0xabcddcba
BROADCAST_UDP_PORT = 13122
DEFAULT_TCP_PORT = 0
NAME_LENGTH = 32

'''represents the player decisions during the game'''
class PlayerDecision(Enum):
    HIT = b"Hittt"
    STAND = b"Stand"

'''represents the message type that can be sent over the network'''
class MessageType(Enum):
    OFFER = 0x2
    REQUEST = 0x3
    RESPONSE = 0x4

'''represents the state of the game'''
class GameState(Enum):
    NOT_OVER = 0x0
    TIE = 0x1
    LOSS = 0x2
    WIN = 0x3

'''represents the suits of the cards'''
class Suits(Enum):
    HEART = 0x0
    DIAMOND = 0x1
    CLUB = 0x2
    SPADE = 0x3
'''represents the formats of each message type'''
class MessageFormat(Enum):
    OFFER = "!IBH32s"       # magic cookie + type + tcp port + server name
    REQUEST = "!IBB32s"     # magic cookie + type + num rounds + client name
    CLIENT_PAYLOAD = "!IB5s"   # magic cookie + type + player decision
    SERVER_PAYLOAD = "!IB3sB"  # magic cookie + type + card(3) + round result

'''represents the length of each message type'''
class MessageLength(Enum):
    OFFER = struct.calcsize(MessageFormat.OFFER.value)
    REQUEST = struct.calcsize(MessageFormat.REQUEST.value)
    CLIENT_PAYLOAD = struct.calcsize(MessageFormat.CLIENT_PAYLOAD.value)
    SERVER_PAYLOAD = struct.calcsize(MessageFormat.SERVER_PAYLOAD.value)

def card_value(rank: int) -> int:
    if 2 <= rank <= 10:
        return rank
    elif 11 <= rank <= 13:  # J, Q, K
        return 10
    elif rank == 1:  # Ace
        return 11


def pack_card(rank: int, suit: int) -> bytes:
    """Pack a card into 3 bytes: 2 bytes rank, 1 byte suit"""
    return struct.pack("!HB", rank, suit)

def unpack_card(card_bytes: bytes) -> tuple[int, int]:
    """Unpack 3 bytes into (rank, suit)"""
    rank, suit = struct.unpack("!HB", card_bytes)
    return rank, suit

def fix_name_length(name: str) -> bytes:
    """Return a 32-byte padded/truncated name"""
    return name.encode()[:NAME_LENGTH].ljust(NAME_LENGTH, b'\x00')

def is_number(s):
    try:
        float(s) # Try converting to a float
        return True
    except ValueError:
        return False