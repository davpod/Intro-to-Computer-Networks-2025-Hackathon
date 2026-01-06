import socket
import struct
import time



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_tcp.bind(('', 0))  # 0 = tell OS to pick a free port
server_tcp.listen()

tcp_port = server_tcp.getsockname()[1]  # retrieve actual port
print("Server listening on TCP port:", tcp_port)

while True:
    offer = struct.pack(
        "!IbH32s",
        MAGIC_COOKIE,
        MSG_OFFER,
        tcp_port,
        b"MyCoolServer".ljust(32, b'\x00')
    )
    sock.sendto(offer, ('255.255.255.255', UDP_PORT))
    time.sleep(1)