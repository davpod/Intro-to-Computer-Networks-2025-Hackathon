# server.py
import socket
from networkManager import *
from my_utils import *
from game import BlackjackGame

SERVER_NAME = "BlackijeckyServer"
ACCEPT_TIMEOUT = 1.0  # seconds


def handle_client(client_sock: socket.socket, client_ip: str):
    """
    Handle a full client session:
    - receive request
    - play num_rounds
    - close connection
    """
    print(f"[SERVER] Client connected from {client_ip}")

    try:
        # ---- receive request ----
        data = safe_recv(client_sock, MessageLength.REQUEST.value)
        num_rounds, client_name = unpack_request(data)
        print(f"[SERVER] Client '{client_name}' requested {num_rounds} rounds")

        # ---- start playing rounds ----
        for round_idx in range(1, num_rounds + 1):
            print(f"[SERVER] Starting round {round_idx}")

            # Create a new round
            game = BlackjackGame()

            # Deal initial hands
            player_hand = [game.draw_card(), game.draw_card()]
            dealer_hand = [game.draw_card(), game.draw_card()]

            print(f"[SERVER] Initial player hand: {player_hand}")
            print(f"[SERVER] Dealer shows: {dealer_hand[0]}")

            # --- Player turn ---
            while True:
                # Check for bust
                if game.hand_value(player_hand) > 21:
                    # Player busts → send final result
                    payload = pack_payload(
                        round_result=GameState.LOSS,
                        card=player_hand[-1]
                    )
                    client_sock.sendall(payload)
                    print("[SERVER] Player busts")
                    break

                # Send last card with NOT_OVER
                payload = pack_payload(
                    round_result=GameState.NOT_OVER,
                    card=player_hand[-1]
                )
                client_sock.sendall(payload)

                # Wait for client decision
                data = safe_recv(client_sock, MessageLength.CLIENT_PAYLOAD.value)
                decision = unpack_payload(data, is_client=True)

                if decision == PlayerDecision.HIT:
                    # Draw new card
                    player_hand.append(game.draw_card())
                    print(f"[SERVER] Player hits, new hand: {player_hand}")
                else:
                    print(f"[SERVER] Player stands with hand: {player_hand}")
                    break

            # --- Dealer turn ---
            if game.hand_value(player_hand) <= 21:
                print(f"[SERVER] Dealer turn, initial hand: {dealer_hand}")
                while game.hand_value(dealer_hand) < 17:
                    dealer_hand.append(game.draw_card())
                    # Send each dealer card to client
                    payload = pack_payload(
                        round_result=GameState.NOT_OVER,
                        card=dealer_hand[-1]
                    )
                    client_sock.sendall(payload)
                    print(f"[SERVER] Dealer draws: {dealer_hand[-1]}")

                # --- Decide winner ---
                player_total = game.hand_value(player_hand)
                dealer_total = game.hand_value(dealer_hand)
                if dealer_total > 21:
                    result = GameState.WIN
                elif player_total > dealer_total:
                    result = GameState.WIN
                elif player_total < dealer_total:
                    result = GameState.LOSS
                else:
                    result = GameState.TIE

                # Send final card + result
                payload = pack_payload(
                    round_result=result,
                    card=dealer_hand[-1]
                )
                client_sock.sendall(payload)
                print(f"[SERVER] Round result: {result}")

        print(f"[SERVER] Finished session with {client_name}")

    except (ConnectionError, ValueError, socket.timeout) as e:
        print(f"[SERVER] Client error: {e}")

    finally:
        client_sock.close()
        print(f"[SERVER] Connection closed for {client_ip}")


def main():
    # ---- create TCP server ----
    server_sock = create_tcp_server()
    tcp_port = server_sock.getsockname()[1]

    print(f"[SERVER] Server started, listening on TCP port {tcp_port}")

    # ---- main server loop ----
    while True:
        # 1. broadcast offer once
        broadcast_offer_once(SERVER_NAME, tcp_port)
        print("[SERVER] Offer broadcasted")

        # 2. wait for client with timeout
        client_sock, client_ip = accept_tcp_connection_with_timeout(
            server_sock, ACCEPT_TIMEOUT
        )

        # 3. no client → go back to broadcast
        if client_sock is None:
            continue

        # 4. client connected → handle session
        handle_client(client_sock, client_ip)


if __name__ == "__main__":
    main()
