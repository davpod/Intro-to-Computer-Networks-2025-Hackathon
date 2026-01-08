# server.py
import socket
from networkManager import *
from my_utils import *
from game import BlackjackGame

SERVER_NAME = "BlackijeckyServer"
ACCEPT_TIMEOUT = 1.0  # seconds


def handle_client(client_sock: socket.socket, client_ip: str):
    print(f"[SERVER] Client connected from {client_ip}")

    try:
        # ---- receive request ----
        data = safe_recv(client_sock, MessageLength.REQUEST.value)
        num_rounds, client_name = unpack_request(data)

        print(f"[SERVER] Client '{client_name}' requested {num_rounds} rounds")

        for round_idx in range(1, num_rounds + 1):
            print(f"\n[SERVER] === Round {round_idx} ===")

            game = BlackjackGame()

            player_hand = [game.draw_card(), game.draw_card()]
            dealer_hand = [game.draw_card(), game.draw_card()]

            print("[SERVER] Player cards:", ", ".join(map(str, player_hand)))
            print("[SERVER] Dealer shows:", dealer_hand[0])

            # ---- send initial 3 cards ----
            for card in player_hand:
                client_sock.sendall(
                    pack_server_payload(card, GameState.NOT_OVER)
                )

            client_sock.sendall(
                pack_server_payload(dealer_hand[0], GameState.NOT_OVER)
            )

            # ---- player turn ----
            while True:
                if sum(c.value() for c in player_hand) > 21:
                    print("[SERVER] Player busts")
                    client_sock.sendall(
                        pack_server_payload(player_hand[-1], GameState.LOSS)
                    )
                    break

                decision = unpack_client_payload(
                    safe_recv(client_sock, MessageLength.CLIENT_PAYLOAD.value)
                )

                if decision == PlayerDecision.HIT:
                    card = game.draw_card()
                    player_hand.append(card)
                    print("[SERVER] Player hits:", card)
                    print("[SERVER] Player cards:", ", ".join(map(str, player_hand)))
                    print("[SERVER] Dealer shows:", dealer_hand[0])
                    if sum(c.value() for c in player_hand) > 21:
                        client_sock.sendall(
                            pack_server_payload(card, GameState.LOSS)
                        )
                        break
                    client_sock.sendall(
                        pack_server_payload(card, GameState.NOT_OVER)
                    )
                else:
                    print("[SERVER] Player stands")
                    break

            # ---- dealer turn ----
            if sum(c.value() for c in player_hand) <= 21:
                # reveal hidden card
                print("[SERVER] Dealer reveals:", dealer_hand[1])
                if sum(c.value() for c in dealer_hand) < 17:
                    client_sock.sendall(
                        pack_server_payload(dealer_hand[1], GameState.NOT_OVER)
                    )

                #draw for as long as needed
                while sum(c.value() for c in dealer_hand) < 17:
                    card = game.draw_card()
                    dealer_hand.append(card)
                    print("[SERVER] Dealer hits:", card)

                    if sum(c.value() for c in dealer_hand) < 17:
                        client_sock.sendall(
                            pack_server_payload(card, GameState.NOT_OVER)
                        )

                # ---- decide result ----
                p = sum(c.value() for c in player_hand)
                d = sum(c.value() for c in dealer_hand)

                if d > 21 or p > d:
                    result = GameState.WIN
                elif p < d:
                    result = GameState.LOSS
                else:
                    result = GameState.TIE
                print("[SERVER] Player cards:", ", ".join(map(str, player_hand)))
                print("[SERVER] Dealer shows:", dealer_hand)
                print(f"[SERVER] Player card values sum: {sum(c.value() for c in player_hand)}")
                print(f"[SERVER] Dealer card values sum: {sum(c.value() for c in dealer_hand)}")
                print(f"[SERVER] Result: {result.name}")
                client_sock.sendall(
                    pack_server_payload(dealer_hand[-1], result)
                )

        print(f"\n[SERVER] Finished session with {client_name}")

    except (ConnectionError, ValueError, socket.timeout) as e:
        print(f"[SERVER] Client error: {e}")

    finally:
        client_sock.close()
        print(f"[SERVER] Connection closed for {client_ip}")


def main():
    server_sock = create_tcp_server()
    tcp_port = server_sock.getsockname()[1]

    print(f"[SERVER] Server started, listening on TCP port {tcp_port}")

    while True:
        print(f"[SERVER] Broadcasting offer")
        broadcast_offer(SERVER_NAME, tcp_port)
        client_sock, client_ip = accept_tcp_connection_with_timeout(
            server_sock, ACCEPT_TIMEOUT
        )

        if client_sock is None:
            continue

        handle_client(client_sock, client_ip)


if __name__ == "__main__":
    main()
