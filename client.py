import socket
from my_utils import *

NAME="do i really need a name?"
offer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if hasattr(socket, "SO_REUSEPORT"):
    offer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
else:
    offer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

offer_sock.bind(('', BROADCAST_UDP_PORT))



while True:
    user_input=input("enter how many rounds you want to play, to quit enter quit:")
    if user_input.lower() == "quit":
        quit=True
        offer_sock.close()
        break
    if user_input.isdigit() and int(user_input) > 0:#the good path
        rounds_number = int(user_input)



    else:
        print("pls enter a valid non negative integer or 'quit'")


