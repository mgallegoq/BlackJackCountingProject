from core.cards import Card, Rank

class HiLoCounter:
    def __init__(self, total_decks: int):
        self.total_decks = total_decks
        self.running_count = 0
        self.cards_seen = 0
        self.trace = []  # (card, delta, running_count)

    def observe(self, card: Card) -> None:
        delta = self._delta(card)
        self.running_count += delta
        self.cards_seen += 1
        self.trace.append((card, delta, self.running_count))

    def _delta(self, card: Card) -> int:
        if card.rank in {
            Rank.TWO, Rank.THREE, Rank.FOUR,
            Rank.FIVE, Rank.SIX
        }:
            return 1
        if card.rank in {
            Rank.TEN, Rank.JACK, Rank.QUEEN,
            Rank.KING, Rank.ACE
        }:
            return -1
        return 0

    @property
    def decks_remaining(self) -> float:
        remaining_cards = self.total_decks * 52 - self.cards_seen
        return max(remaining_cards / 52, 0.25)

    @property
    def true_count(self) -> float:
        return self.running_count / self.decks_remaining
