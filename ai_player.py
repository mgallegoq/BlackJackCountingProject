# ai_player.py
import os
from core.rounds import GameRound
from core.rules import dealer_should_hit, BlackjackRules
from core.shoe import Shoe
from counting.hilo import HiLoCounter

# ---------------------------
# Win tracking
# ---------------------------
WIN_FILE = "ai_win_history.txt"

def load_history():
    if not os.path.exists(WIN_FILE):
        return {"wins": 0, "hands": 0}
    with open(WIN_FILE, "r") as f:
        lines = f.read().splitlines()
        if len(lines) != 2:
            return {"wins": 0, "hands": 0}
        return {"wins": int(lines[0]), "hands": int(lines[1])}

def save_history(history):
    with open(WIN_FILE, "w") as f:
        f.write(f"{history['wins']}\n{history['hands']}\n")

# ---------------------------
# Card value mapping
# ---------------------------
def card_value(card):
    if card.rank.value in ["J", "Q", "K"]:
        return 10
    if card.rank.value == "A":
        return 11
    return int(card.rank.value)

# ---------------------------
# Basic strategy tables
# ---------------------------
def basic_strategy(player_hand, dealer_card, tc):
    """
    Returns the action: 'h', 's', 'd', or 'p' (split)
    Simplified full table:
    - Hard totals
    - Soft totals
    - Pairs (splits)
    - TC deviations included
    """
    best_total = player_hand.best_total
    dealer_value = card_value(dealer_card)

    # Splits (example: split 8s or Aces)
    if len(player_hand.cards) == 2 and player_hand.cards[0].rank.value == player_hand.cards[1].rank.value:
        pair = player_hand.cards[0].rank.value
        if pair in ["A", "8"]:
            return 'p'  # split Aces and 8s always
        if pair in ["2","3","7"] and dealer_value <=7:
            return 'p'
        if pair == "6" and dealer_value <=6:
            return 'p'
        if pair == "9" and dealer_value not in [7,10,11]:
            return 'p'
        if pair == "4" and dealer_value in [5,6]:
            return 'p'
        if pair == "5":
            return 'd'
        if pair in ["10","J","Q","K"]:
            return 's'

    # Soft totals
    if any(c.rank.value == "A" for c in player_hand.cards) and best_total <=21:
        # Soft totals A2-A7
        if best_total == 19 or best_total == 20:
            return 's'
        if best_total == 18:
            if dealer_value in [9,10,11]:
                return 'h'
            else:
                return 's'
        if best_total <=17:
            if dealer_value in [3,4,5,6]:
                return 'd'
            else:
                return 'h'

    # Hard totals
    if best_total >=17:
        return 's'
    if best_total >=13 and dealer_value <=6:
        return 's'
    if best_total ==12 and 4<=dealer_value<=6:
        return 's'
    if best_total ==11:
        return 'd'
    if best_total ==10 and dealer_value <=9:
        return 'd'
    if best_total ==9 and 3<=dealer_value<=6:
        return 'd'
    if best_total <=8:
        return 'h'

    # TC deviations (examples)
    if best_total==16 and dealer_value==10 and tc>=0:
        return 's'
    if best_total==15 and dealer_value==10 and tc>=4:
        return 's'

    return 'h'

# ---------------------------
# Render hand
# ---------------------------
def render_hand(hand):
    return " ".join(f"{c.rank.value}{c.suit.value}" for c in hand.cards)

# ---------------------------
# Simulation parameters
# ---------------------------
NUM_HANDS = 100000
shoe = Shoe(decks=6)
rules = BlackjackRules()
rules.validate()
counter = HiLoCounter(total_decks=rules.decks)

# Load historical stats
history = load_history()
session_hands = 0
session_wins = 0

print(f"Historical win rate: {history['wins']}/{history['hands']} = "
      f"{100*history['wins']/history['hands']:.2f}%" if history['hands']>0 else "No historical data yet.")

# ---------------------------
# Main simulation loop
# ---------------------------
for i in range(NUM_HANDS):
    # Reshuffle if shoe is low
    if shoe.cards_remaining < 15:
        shoe = Shoe(decks=6)
        counter = HiLoCounter(total_decks=rules.decks)

    round = GameRound(shoe, rules)
    round.initial_deal()
    for card in round.exposed_cards:
        counter.observe(card)

    # Player turn
    while True:
        action = basic_strategy(round.player_hand, round.dealer_hand.cards[0], counter.true_count)
        if action == 'h':
            round.player_hit()
            counter.observe(round.exposed_cards[-1])
        elif action == 's':
            break
        elif action == 'd':
            round.player_hit()
            counter.observe(round.exposed_cards[-1])
            break
        elif action == 'p':
            # For now: split as two hands, simplified
            break

        if round.player_hand.best_total is None or round.player_hand.best_total>=21:
            break

    # Dealer turn
    round.reveal_dealer_hole_card()
    counter.observe(round.exposed_cards[-1])
    while dealer_should_hit(round.dealer_hand.totals, round.dealer_hand.is_soft, rules):
        round.dealer_hit()
        counter.observe(round.exposed_cards[-1])

    # Resolve outcome
    player_best = round.player_hand.best_total
    dealer_best = round.dealer_hand.best_total

    if player_best is not None and (dealer_best is None or player_best>dealer_best):
        session_wins+=1
        history['wins']+=1

    session_hands+=1
    history['hands']+=1
    save_history(history)

    # Logging
    print(f"\nHand {i+1}")
    print("Player:", render_hand(round.player_hand), "->", player_best)
    print("Dealer:", render_hand(round.dealer_hand), "->", dealer_best)
    print(f"Running count: {counter.running_count}, True count: {counter.true_count:.2f}")
    print(f"Session win rate: {session_wins}/{session_hands} = {100*session_wins/session_hands:.2f}%")
    print(f"Historical win rate: {history['wins']}/{history['hands']} = {100*history['wins']/history['hands']:.2f}%")
