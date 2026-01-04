# play_test.py
from core.rounds import GameRound
from core.rules import dealer_should_hit, BlackjackRules
from core.shoe import Shoe
from counting.hilo import HiLoCounter

# ---------------------------
# Helper: render hands
# ---------------------------
def render_hand(hand, hide_second_card=False):
    """
    Returns a human-readable string for a hand.
    hide_second_card=True hides the dealer hole card.
    """
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

round = GameRound(shoe, rules)
round.initial_deal()

# Observe initial exposed cards
for card in round.exposed_cards:
    counter.observe(card)

# ---------------------------
# Show initial deal
# ---------------------------
print("\n--- INITIAL DEAL ---")
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

    choice = input("\nHit or Stand? (h/s): ").strip().lower()

    if choice == "h":
        round.player_hit()
        card = round.exposed_cards[-1]
        counter.observe(card)
        print("\nPlayer hits.")
        print("Player:", render_hand(round.player_hand))
        print("Player totals:", round.player_hand.totals)

    elif choice == "s":
        print("\nPlayer stands.")
        break

    else:
        print("Invalid input. Enter 'h' or 's'.")

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
elif dealer_best is None:
    print("Dealer busts. Player wins.")
elif player_best > dealer_best:
    print("Player wins!")
elif player_best < dealer_best:
    print("Dealer wins!")
else:
    print("Push (tie).")

# ---------------------------
# Show counts
# ---------------------------
print("\n--- COUNT ---")
print(f"Running count: {counter.running_count}")
print(f"True count: {counter.true_count:.2f}")
