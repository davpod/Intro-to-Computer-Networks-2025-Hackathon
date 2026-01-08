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

def pack_card(rank: int, suit: int) -> bytes:
    """Pack a card into 3 bytes: 2 bytes rank, 1 byte suit"""
    return struct.pack("!HB", rank, suit)

def unpack_card(card_bytes: bytes):
    """Unpack 3 bytes into (rank, suit)"""
    rank, suit = struct.unpack("!HB", card_bytes)
    try:
        return Card(rank, Suits(suit))
    except ValueError:
        raise ValueError("Invalid suit received")

def fix_name_length(name: str) -> bytes:
    """Return a 32-byte padded/truncated name"""
    return name.encode()[:NAME_LENGTH].ljust(NAME_LENGTH, b'\x00')

'''check if given input is a number'''
def is_number(s):
    try:
        float(s) # Try converting to a float
        return True
    except ValueError:
        return False

'''encapsulate ranks and suits into a single card'''
class Card:
    def __init__(self, rank: int, suit: Suits):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        # Convert rank to nice string
        rank_str = {1: "A", 11: "J", 12: "Q", 13: "K"}.get(self.rank, str(self.rank))
        # Suit as a symbol
        suit_str = {"HEART": "♥", "DIAMOND": "♦", "CLUB": "♣", "SPADE": "♠"}[self.suit.name]
        return f"{rank_str}{suit_str}"

    def __repr__(self):
        return str(self)

    def value(self):
        """Return the blackjack value of the card"""
        if 2 <= self.rank <= 10:
            return self.rank
        elif 11 <= self.rank <= 13:  # J,Q,K
            return 10
        elif self.rank == 1:  # Ace
            return 11