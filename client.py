# client.py
import sys
from networkManager import *
from my_utils import *


CLIENT_NAME = "BlackijeckyClient"


def prompt_num_rounds() -> int:
    while True:
        choice = input("Enter number of rounds to play (or 'q' to quit): ").strip().lower()
        if choice == "q":
            return 0
        if choice.isdigit() and int(choice) > 0:
            return int(choice)
        print("[CLIENT] Invalid input. Please enter a positive number or 'q'.")


def ask_player_decision() -> PlayerDecision:
    while True:
        action = input("Choose action [H]it / [S]tand: ").strip().lower()
        if action in ("h", "hit"):
            return PlayerDecision.HIT
        if action in ("s", "stand"):
            return PlayerDecision.STAND
        print("[CLIENT] Invalid input.")


def play_game(tcp_sock: socket.socket, num_rounds: int):
    stats = {"wins": 0, "losses": 0, "ties": 0}

    # ---- send request ----
    tcp_sock.sendall(pack_request(num_rounds, CLIENT_NAME))

    for round_idx in range(1, num_rounds + 1):
        print(f"\n[CLIENT] ===== Round {round_idx} =====")

        player_hand: list[Card] = []
        dealer_hand: list[Card] = []

        # ---- INITIAL DEAL: 3 cards ----
        for i in range(3):
            data = safe_recv(tcp_sock, MessageLength.SERVER_PAYLOAD.value)
            card, state = unpack_server_payload(data)

            if i < 2:
                player_hand.append(card)
            else:
                dealer_hand.append(card)

        print(f"[CLIENT] Your hand: {', '.join(map(str, player_hand))}")
        print(f"[CLIENT] Your card values sum: {sum(c.value() for c in player_hand)}")
        print(f"[CLIENT] Dealer shows: {dealer_hand[0]}")

        # ---- PLAYER TURN ----
        round_over = False
        while not round_over:
            # ask player for action
            decision = ask_player_decision()
            tcp_sock.sendall(pack_client_payload(decision))

            if decision == PlayerDecision.STAND:
                break  # exit player's turn loop

            # if HIT, receive next card
            data = safe_recv(tcp_sock, MessageLength.SERVER_PAYLOAD.value)
            card, state = unpack_server_payload(data)
            player_hand.append(card)
            print(f"[CLIENT] You drew: {card}")
            print(f"[CLIENT] Your hand: {', '.join(map(str, player_hand))}")
            print(f"[CLIENT] Your card values sum: {sum(c.value() for c in player_hand)}")
            print(f"[CLIENT] Dealer shows: {dealer_hand[0]}")
            if state != GameState.NOT_OVER:
                # round ended immediately after HIT (bust)
                if state == GameState.WIN:
                    stats["wins"] += 1
                    print("[CLIENT] You won this round!")
                elif state == GameState.LOSS:
                    stats["losses"] += 1
                    print("[CLIENT] You lost this round.")
                else:
                    stats["ties"] += 1
                    print("[CLIENT] This round is a tie.")
                round_over = True
                break

        # ---- DEALER TURN ----
        while not round_over:
            data = safe_recv(tcp_sock, MessageLength.SERVER_PAYLOAD.value)
            card, state = unpack_server_payload(data)
            dealer_hand.append(card)
            print(f"[CLIENT] Dealer drew: {card}")
            print(f"[CLIENT] Your hand: {', '.join(map(str, player_hand))}")
            print(f"[CLIENT] Your card values sum: {sum(c.value() for c in player_hand)}")
            print(f"[CLIENT] Dealer shows: {', '.join(map(str, dealer_hand))}")
            print(f"[CLIENT] Dealer card values sum: {sum(c.value() for c in dealer_hand)}")
            if state != GameState.NOT_OVER:
                if state == GameState.WIN:
                    stats["wins"] += 1
                    print("[CLIENT] You won this round!")
                elif state == GameState.LOSS:
                    stats["losses"] += 1
                    print("[CLIENT] You lost this round.")
                else:
                    stats["ties"] += 1
                    print("[CLIENT] This round is a tie.")
                round_over = True
                break

        # ---- round summary ----
        total_played = sum(stats.values())
        win_ratio = stats["wins"] / total_played if total_played else 0
        print(f"[CLIENT] Win ratio so far: {win_ratio:.2f}")

    # ---- all rounds done ----
    total_played = sum(stats.values())
    print("\n[CLIENT] ===== Game Over =====")
    print(f"[CLIENT] Played: {total_played}")
    print(f"[CLIENT] Wins: {stats['wins']}")
    print(f"[CLIENT] Losses: {stats['losses']}")
    print(f"[CLIENT] Ties: {stats['ties']}")
    print(f"[CLIENT] Final win ratio: {stats['wins'] / total_played:.2f}")


def main():
    print("[CLIENT] Blackijecky Client started")

    while True:
        num_rounds = prompt_num_rounds()
        if num_rounds == 0:
            print("[CLIENT] Exiting gracefully.")
            sys.exit(0)

        print("[CLIENT] Listening for server offers...")
        try:
            server_ip, tcp_port, server_name = listen_for_offers(timeout=5.0)
        except socket.timeout:
            print("[CLIENT] No offers received.")
            continue

        print(f"[CLIENT] Connecting to {server_name} at {server_ip}:{tcp_port}")
        try:
            tcp_sock = connect_to_tcp_server(server_ip, tcp_port)
        except Exception as e:
            print("[CLIENT] Connection failed:", e)
            continue

        try:
            play_game(tcp_sock, num_rounds)
        except Exception as e:
            print("[CLIENT] Game error:", e)
        finally:
            tcp_sock.close()
            print("[CLIENT] Disconnected.\n")


if __name__ == "__main__":
    main()
