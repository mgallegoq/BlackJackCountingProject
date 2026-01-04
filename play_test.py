# play_test.py
import os
from core.rounds import GameRound
from core.rules import dealer_should_hit, BlackjackRules
from core.shoe import Shoe
from counting.hilo import HiLoCounter

# ---------------------------
# Config: win tracking file
# ---------------------------
WIN_FILE = "win_history.txt"

def load_history():
    if not os.path.exists(WIN_FILE):
        return {"wins": 0, "hands": 0}
    with open(WIN_FILE, "r") as f:
        lines = f.read().splitlines()
        if len(lines) != 2:
            return {"wins": 0, "hands": 0}
        wins = float(lines[0])
        hands = float(lines[1])
        return {"wins": wins, "hands": hands}

def save_history(history):
    with open(WIN_FILE, "w") as f:
        f.write(f"{history['wins']}\n{history['hands']}\n")

# ---------------------------
# Helper: render hands
# ---------------------------
def render_hand(hand, hide_second_card=False):
    rendered = []
    for i, card in enumerate(hand.cards):
        if hide_second_card and i == 1:
            rendered.append("??")
        else:
            rendered.append(f"{card.rank.value}{card.suit.value}")
    return " ".join(rendered)

# ---------------------------
# Initialize game objects
# ---------------------------
shoe = Shoe(decks=6)
rules = BlackjackRules()
rules.validate()

counter = HiLoCounter(total_decks=rules.decks)

# Load historical wins
history = load_history()
session_hands = 0
session_wins = 0

print(f"Historical win rate: {history['wins']}/{history['hands']} "
      f"= {100*history['wins']/history['hands']:.2f}%"
      if history['hands'] > 0 else "No historical data yet.")

# ---------------------------
# Main game loop
# ---------------------------
while True:
    # Check shoe remaining cards
    if shoe.cards_remaining < 15:
        print("\nNot enough cards remaining in the shoe. Reshuffling...")
        shoe = Shoe(decks=6)
        counter = HiLoCounter(total_decks=rules.decks)

    round = GameRound(shoe, rules)
    round.initial_deal()

    for card in round.exposed_cards:
        counter.observe(card)

    # Show initial deal
    print("\n--- NEW HAND ---")
    print("Dealer:", render_hand(round.dealer_hand, hide_second_card=True))
    print("Player:", render_hand(round.player_hand))
    print("Player totals:", round.player_hand.totals)

    # ---------------------------
    # Player turn
    # ---------------------------
    while True:
        best = round.player_hand.best_total

        if best is None:
            print("\nPlayer busts!")
            break
        if best == 21:
            print("\nPlayer stands on 21!")
            break

        choice = input("\nHit or Stand? (h/s, q to quit): ").strip().lower()

        if choice == "h":
            round.player_hit()
            card = round.exposed_cards[-1]
            counter.observe(card)
            print("\nPlayer hits.")
            print("Dealer:", render_hand(round.dealer_hand, hide_second_card=True))
            print("Player:", render_hand(round.player_hand))
            print("Player totals:", round.player_hand.totals)

        elif choice == "s":
            print("\nPlayer stands.")
            break

        elif choice == "q":
            print("Exiting game.")
            exit()

        else:
            print("Invalid input. Enter 'h', 's', or 'q'.")

    # ---------------------------
    # Dealer turn
    # ---------------------------
    round.reveal_dealer_hole_card()
    counter.observe(round.exposed_cards[-1])

    print("\n--- DEALER REVEALS ---")
    print("Dealer:", render_hand(round.dealer_hand))
    print("Dealer totals:", round.dealer_hand.totals)

    while dealer_should_hit(round.dealer_hand.totals, round.dealer_hand.is_soft, rules):
        round.dealer_hit()
        card = round.exposed_cards[-1]
        counter.observe(card)
        print("\nDealer hits.")
        print("Dealer:", render_hand(round.dealer_hand))
        print("Dealer totals:", round.dealer_hand.totals)

    # ---------------------------
    # Resolve outcome
    # ---------------------------
    player_best = round.player_hand.best_total
    dealer_best = round.dealer_hand.best_total

    print("\n--- FINAL RESULT ---")
    if player_best is None:
        print("Player busts. Dealer wins.")
        hand_won = False
        tie = False
    elif dealer_best is None:
        print("Dealer busts. Player wins.")
        hand_won = True
    elif player_best > dealer_best:
        print("Player wins!")
        hand_won = True
    elif player_best < dealer_best:
        print("Dealer wins!")
        hand_won = False
        tie = False
    else:
        print("Push (tie).")
        hand_won = False
        tie = True

    # ---------------------------
    # Update counters
    # ---------------------------
    session_hands += 1
    if hand_won:
        session_wins += 1
        history['wins'] += 1
    elif tie:
        session_wins += .5
        history['wins'] += 0.5
    history['hands'] += 1
    save_history(history)

    # ---------------------------
    # Show counts
    # ---------------------------
    print("\n--- COUNT ---")
    print(f"Running count: {counter.running_count}")
    print(f"True count: {counter.true_count:.2f}")

    # ---------------------------
    # Show win stats
    # ---------------------------
    historical_pct = 100 * history['wins'] / history['hands'] if history['hands'] > 0 else 0
    session_pct = 100 * session_wins / session_hands if session_hands > 0 else 0

    print(f"\nHistorical win rate: {history['wins']}/{history['hands']} = {historical_pct:.2f}%")
    print(f"Current session win rate: {session_wins}/{session_hands} = {session_pct:.2f}%")
