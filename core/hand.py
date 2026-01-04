from typing import List, Optional
from .cards import Card

class Hand:
    def __init__(self):
        self.cards: List[Card] = []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    @property
    def totals(self) -> List[int]:
        totals = [0]
        for card in self.cards:
            new_totals = []
            for value in card.blackjack_values:
                for total in totals:
                    new_totals.append(total + value)
            totals = new_totals
        return sorted(set(totals))

    @property
    def best_total(self) -> Optional[int]:
        valid = [t for t in self.totals if t <= 21]
        return max(valid) if valid else None

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and 21 in self.totals

    @property
    def is_bust(self) -> bool:
        return all(t > 21 for t in self.totals)
    @property
    def is_soft(self) -> bool:
        """
        A hand is soft if an ace is counted as 11
        without busting.
        """
        if not self.cards:
            return False

        for total in self.totals:
            if total <= 21:
                ace_as_eleven = 11 in [
                    sum(card.blackjack_values) - 1
                    for card in self.cards
                    if card.rank.name == "ACE"
                ]
                return any(
                    total - 10 == t for t in self.totals
                )

        return False
