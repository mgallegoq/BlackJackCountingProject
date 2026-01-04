import random
from typing import List
from .cards import Card, Suit, Rank

class Shoe:
    def __init__(self, decks: int = 6):
        self.decks = decks
        self._cards = self._build_shoe()
        self.discards: List[Card] = []
        random.shuffle(self._cards)

    def _build_shoe(self) -> List[Card]:
        return [
            Card(rank, suit)
            for _ in range(self.decks)
            for suit in Suit
            for rank in Rank
        ]

    def draw(self) -> Card:
        if not self._cards:
            raise RuntimeError("Shoe is empty")
        card = self._cards.pop()
        self.discards.append(card)
        return card

    @property
    def cards_remaining(self) -> int:
        return len(self._cards)
