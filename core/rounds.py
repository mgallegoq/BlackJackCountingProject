from typing import List
from .cards import Card
from .hand import Hand
from .shoe import Shoe

class GameRound:
    def __init__(self, shoe, rules):
        self.shoe = shoe
        self.rules = rules

        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.exposed_cards = []


    def _deal_card(self, hand: Hand, exposed: bool = True) -> None:
        card = self.shoe.draw()
        hand.add_card(card)
        if exposed:
            self.exposed_cards.append(card)

    def initial_deal(self) -> None:
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand)
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand, exposed=False)  # hole card

    def player_hit(self) -> None:
        self._deal_card(self.player_hand)

    def reveal_dealer_hole_card(self) -> None:
        self.exposed_cards.append(self.dealer_hand.cards[1])

    def dealer_hit(self) -> None:
        self._deal_card(self.dealer_hand)
