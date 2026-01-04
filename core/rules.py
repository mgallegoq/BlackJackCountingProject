from dataclasses import dataclass
from enum import Enum

class DealerSoft17Rule(Enum):
    HIT = "hit_soft_17"
    STAND = "stand_soft_17"

@dataclass(frozen=True)
class BlackjackRules:
    """
    Immutable configuration describing a blackjack ruleset.
    """

    decks: int = 6

    blackjack_payout: float = 1.5

    dealer_soft_17: DealerSoft17Rule = DealerSoft17Rule.STAND

    allow_double: bool = True
    allow_double_after_split: bool = True

    allow_split: bool = True
    max_splits: int = 3
    allow_resplit_aces: bool = False

    hit_split_aces: bool = False

    surrender_allowed: bool = False

    def validate(self) -> None:
        """
        Ensures the ruleset is internally consistent.
        Called once at game initialization.
        """
        if self.decks < 1:
            raise ValueError("Number of decks must be >= 1")

        if self.blackjack_payout <= 1.0:
            raise ValueError("Blackjack payout must exceed even money")

        if self.max_splits < 0:
            raise ValueError("max_splits cannot be negative")

        if not self.allow_split and self.max_splits > 0:
            raise ValueError(
                "max_splits > 0 is invalid when splitting is disabled"
            )

def dealer_should_hit(
    hand_totals: list[int],
    is_soft: bool,
    rules: BlackjackRules
) -> bool:
    """
    Determines whether the dealer should hit given current totals.
    """

    best_under = max((t for t in hand_totals if t <= 21), default=None)

    if best_under is None:
        return False  # dealer is bust

    if best_under < 17:
        return True

    if best_under > 17:
        return False

    # exactly 17
    if is_soft and rules.dealer_soft_17 == DealerSoft17Rule.HIT:
        return True

    return False
