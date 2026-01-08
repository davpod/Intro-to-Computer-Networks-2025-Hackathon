# game.py
import random
from my_utils import Suits, card_value, pack_card, unpack_card, GameState, PlayerDecision

class BlackjackGame:
    """
    Handles a single round of simplified Blackjack
    """
    def __init__(self):
        self.deck = self._new_shuffled_deck()

    def _new_shuffled_deck(self) -> list[tuple[int, Suits]]:
        """Create a new standard 52-card deck and shuffle it"""
        deck = [(rank, suit) for suit in Suits for rank in range(1, 14)]
        random.shuffle(deck)
        return deck

    def draw_card(self) -> tuple[int, Suits]:
        """Draw a card from the deck"""
        if not self.deck:
            self.deck = self._new_shuffled_deck()
        return self.deck.pop()

    def hand_value(self, hand: list[tuple[int, Suits]]) -> int:
        """Compute the total value of a hand"""
        total = sum(card_value(rank) for rank, _ in hand)
        return total

    def play_round(self, player_decision_callback) -> tuple[list[tuple[int,Suits]], list[tuple[int,Suits]], GameState]:
        """
        Play a single round:
        - player_decision_callback(): called to get player's choice (HIT/STAND)
        Returns:
        - player_hand
        - dealer_hand
        - result (GameState)
        """

        # --- Initial deal ---
        player_hand = [self.draw_card(), self.draw_card()]
        dealer_hand = [self.draw_card(), self.draw_card()]

        # --- Player turn ---
        while True:
            if self.hand_value(player_hand) > 21:
                # player bust
                return player_hand, dealer_hand, GameState.LOSS

            decision = player_decision_callback(player_hand, dealer_hand[0])
            if decision == PlayerDecision.HIT:
                player_hand.append(self.draw_card())
            else:
                break

        # --- Dealer turn ---
        while self.hand_value(dealer_hand) < 17:
            dealer_hand.append(self.draw_card())

        # --- Determine winner ---
        player_total = self.hand_value(player_hand)
        dealer_total = self.hand_value(dealer_hand)

        if dealer_total > 21:
            return player_hand, dealer_hand, GameState.WIN
        if player_total > dealer_total:
            return player_hand, dealer_hand, GameState.WIN
        if player_total < dealer_total:
            return player_hand, dealer_hand, GameState.LOSS
        return player_hand, dealer_hand, GameState.TIE
