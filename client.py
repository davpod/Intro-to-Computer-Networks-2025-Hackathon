import socket
from my_utils import MAGIC_COOKIE, BROADCAST_UDP_PORT

NAME="do i really need a name?"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if hasattr(socket, "SO_REUSEPORT"):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
else:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(('', BROADCAST_UDP_PORT))

print("Client started, listening for offer requests...")

while True:
    data, addr = sock.recvfrom(1024)   # <-- BLOCKS HERE
    print(f"Received offer from {addr}")
    print(f"Received data {data}")
