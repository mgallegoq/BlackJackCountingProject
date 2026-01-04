from dataclasses import dataclass
from enum import Enum
from typing import List

class Suit(Enum):
    HEARTS = "♥️"
    DIAMONDS = "♦️"
    CLUBS = "♣️"
    SPADES = "♠️"



class Rank(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    @property
    def blackjack_values(self) -> List[int]:
        if self.rank == Rank.ACE:
            return [1, 11]
        if self.rank in {Rank.JACK, Rank.QUEEN, Rank.KING, Rank.TEN}:
            return [10]
        return [int(self.rank.value)]
