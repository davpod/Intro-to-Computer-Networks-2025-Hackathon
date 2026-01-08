# game.py
import random
from typing import List, Callable
from my_utils import Card, Suits, GameState, PlayerDecision


class BlackjackGame:
    """
    Handles a single round of simplified Blackjack.
    Pure game logic – no networking, no printing, no user input.
    """

    def __init__(self):
        self.deck: List[Card] = self._new_shuffled_deck()

    def _new_shuffled_deck(self) -> List[Card]:
        """Create and shuffle a standard 52-card deck"""
        deck = [Card(rank, suit) for suit in Suits for rank in range(1, 14)]
        random.shuffle(deck)
        return deck

    def draw_card(self) -> Card:
        """Draw a card from the deck (reshuffle if empty)"""
        if not self.deck:
            self.deck = self._new_shuffled_deck()
        return self.deck.pop()

    def hand_value(self, hand: List[Card]) -> int:
        """
        Compute blackjack hand value.
        (Ace always counts as 11 in this simplified version)
        """
        return sum(card.value() for card in hand)

    def play_round(
        self,
        player_decision_callback: Callable[[List[Card], Card], PlayerDecision]
    ) -> tuple[List[Card], List[Card], GameState]:
        """
        Play a single blackjack round.

        player_decision_callback(player_hand, dealer_visible_card) -> PlayerDecision

        Returns:
        - player_hand
        - dealer_hand
        - GameState (WIN / LOSS / TIE)
        """

        # --- Initial deal ---
        player_hand = [self.draw_card(), self.draw_card()]
        dealer_hand = [self.draw_card(), self.draw_card()]

        # --- Player turn ---
        while True:
            if self.hand_value(player_hand) > 21:
                # Player busts
                return player_hand, dealer_hand, GameState.LOSS

            decision = player_decision_callback(player_hand, dealer_hand[0])

            if decision == PlayerDecision.HIT:
                player_hand.append(self.draw_card())
            else:  # STAND
                break

        # --- Dealer turn ---
        while self.hand_value(dealer_hand) < 17:
            dealer_hand.append(self.draw_card())

        # --- Decide winner ---
        player_total = self.hand_value(player_hand)
        dealer_total = self.hand_value(dealer_hand)

        if dealer_total > 21:
            return player_hand, dealer_hand, GameState.WIN
        if player_total > dealer_total:
            return player_hand, dealer_hand, GameState.WIN
        if player_total < dealer_total:
            return player_hand, dealer_hand, GameState.LOSS
        return player_hand, dealer_hand, GameState.TIE
