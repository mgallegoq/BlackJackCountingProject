# ai_player_strong.py
import os
from core.rounds import GameRound
from core.rules import dealer_should_hit, BlackjackRules
from core.shoe import Shoe
from counting.hilo import HiLoCounter
from copy import deepcopy

# ---------------------------
# Config
# ---------------------------
WIN_FILE = "ai_strong_history.txt"
BASE_BET = 1
INITIAL_BANKROLL = 5000
NUM_HANDS = 50000

# ---------------------------
# Win tracking
# ---------------------------
def load_history():
    if not os.path.exists(WIN_FILE):
        return {"wins": 0, "hands": 0}
    with open(WIN_FILE, "r") as f:
        lines = f.read().splitlines()
        if len(lines)!=2:
            return {"wins":0,"hands":0}
        return {"wins": int(lines[0]), "hands": int(lines[1])}

def save_history(history):
    with open(WIN_FILE, "w") as f:
        f.write(f"{history['wins']}\n{history['hands']}\n")

# ---------------------------
# Card value
# ---------------------------
def card_value(card):
    if card.rank.value in ["J","Q","K"]:
        return 10
    if card.rank.value=="A":
        return 11
    return int(card.rank.value)

# ---------------------------
# Render hand
# ---------------------------
def render_hand(hand):
    return " ".join(f"{c.rank.value}{c.suit.value}" for c in hand.cards)

# ---------------------------
# Full basic strategy with TC deviations
# ---------------------------
def basic_strategy(player_hand, dealer_card, tc):
    """
    Returns action: 'h', 's', 'd', 'p'
    Implements hard totals, soft totals, splits, and key TC deviations
    """
    best_total = player_hand.best_total
    dealer_value = card_value(dealer_card)
    cards = player_hand.cards

    if best_total is None:
        return 's'  # busted

    # -------------------
    # Splits
    # -------------------
    if len(cards)==2 and cards[0].rank.value == cards[1].rank.value:
        pair = cards[0].rank.value
        # Aces and 8s always split
        if pair in ["A","8"]:
            return 'p'
        if pair in ["2","3","7"] and dealer_value<=7:
            return 'p'
        if pair=="6" and dealer_value<=6:
            return 'p'
        if pair=="9" and dealer_value not in [7,10,11]:
            return 'p'
        if pair=="4" and dealer_value in [5,6]:
            return 'p'
        if pair=="5":
            return 'd'
        if pair in ["10","J","Q","K"]:
            return 's'

    # -------------------
    # Soft totals (A + X)
    # -------------------
    has_ace = any(c.rank.value=="A" for c in cards)
    if has_ace and best_total<=21:
        # soft 19-20
        if best_total>=19:
            return 's'
        # soft 18
        if best_total==18:
            if dealer_value in [9,10,11]:
                return 'h'
            else:
                return 's'
        # soft 13-17
        if 13<=best_total<=17:
            if dealer_value in [3,4,5,6]:
                return 'd'
            else:
                return 'h'

    # -------------------
    # Hard totals
    # -------------------
    if best_total >=17:
        return 's'
    if 13<=best_total<=16 and dealer_value<=6:
        return 's'
    if best_total==12 and 4<=dealer_value<=6:
        return 's'
    if best_total==11:
        return 'd'
    if best_total==10 and dealer_value<=9:
        return 'd'
    if best_total==9 and 3<=dealer_value<=6:
        return 'd'
    if best_total<=8:
        return 'h'

    # -------------------
    # TC deviations
    # -------------------
    if best_total==16 and dealer_value==10 and tc>=0:
        return 's'
    if best_total==15 and dealer_value==10 and tc>=4:
        return 's'
    if best_total==10 and dealer_value==11 and tc>=4:
        return 'd'
    if best_total==12 and dealer_value==3 and tc>=2:
        return 's'
    if best_total==12 and dealer_value==2 and tc>=3:
        return 's'

    return 'h'

# ---------------------------
# Bet sizing
# ---------------------------
def bet_for_tc(tc, base_bet, bankroll):
    if tc<=0:
        bet = base_bet
    elif tc==1:
        bet = 2*base_bet
    elif tc==2:
        bet = 3*base_bet
    elif tc==3:
        bet = 4*base_bet
    else:
        bet = 5*base_bet
    bet = min(bet, bankroll)  # cannot bet more than bankroll
    bet = max(bet, 1)         # minimum bet
    return bet

# ---------------------------
# Initialize game
# ---------------------------
shoe = Shoe(decks=6)
rules = BlackjackRules()
rules.validate()
counter = HiLoCounter(total_decks=rules.decks)
bankroll = INITIAL_BANKROLL

history = load_history()
session_hands = 0
session_wins = 0

print(f"Historical win rate: {history['wins']}/{history['hands']} = "
      f"{100*history['wins']/history['hands']:.2f}%" if history['hands']>0 else "No historical data yet.")

# ---------------------------
# Simulation loop
# ---------------------------
for i in range(NUM_HANDS):
    # Reshuffle if low
    if shoe.cards_remaining<15:
        shoe = Shoe(decks=6)
        counter = HiLoCounter(total_decks=rules.decks)
        print("\n--- Shoe reshuffled ---")

    round = GameRound(shoe, rules)
    round.initial_deal()
    for card in round.exposed_cards:
        counter.observe(card)

    # Determine bet
    tc = -counter.true_count
    bet = bet_for_tc(tc, BASE_BET, bankroll)
    print(f"\nHand {i+1}, True count: {tc:.2f}, Bet: {bet}, Bankroll: {bankroll}")

    # ---------------------------
    # Dealer blackjack check first
    # ---------------------------
    dealer_blackjack = len(round.dealer_hand.cards)==2 and round.dealer_hand.best_total==21
    player_blackjack = len(round.player_hand.cards)==2 and round.player_hand.best_total==21

    if dealer_blackjack:
        if player_blackjack:
            hand_won = False  # push
        else:
            bankroll -= bet
            hand_won = False
    elif player_blackjack:
        bankroll += 1.5*bet
        hand_won = True
    else:
        # ---------------------------
        # Player turn
        # ---------------------------
        hands_to_play = [round.player_hand]  # handle splits as separate hands
        hand_results = []

        while hands_to_play:
            current_hand = hands_to_play.pop(0)
            while True:
                action = basic_strategy(current_hand, round.dealer_hand.cards[0], tc)
                if action=='h':
                    round.player_hand = current_hand  # ensure correct reference
                    round.player_hit()
                    counter.observe(round.exposed_cards[-1])
                elif action=='s':
                    break
                elif action=='d':
                    round.player_hand = current_hand
                    round.player_hit()
                    counter.observe(round.exposed_cards[-1])
                    break
                elif action=='p':
                    # split logic: create two hands
                    c1 = deepcopy(current_hand)
                    c2 = deepcopy(current_hand)
                    c1.cards = [current_hand.cards[0]]
                    c2.cards = [current_hand.cards[1]]
                    # draw one card each
                    c1.cards.append(round.shoe.draw())
                    c2.cards.append(round.shoe.draw())
                    hands_to_play.append(c1)
                    hands_to_play.append(c2)
                    break

                if current_hand.best_total is None or current_hand.best_total>=21:
                    break

            hand_results.append(current_hand)

        # ---------------------------
        # Dealer turn
        # ---------------------------
        round.reveal_dealer_hole_card()
        counter.observe(round.exposed_cards[-1])
        while dealer_should_hit(round.dealer_hand.totals, round.dealer_hand.is_soft, rules):
            round.dealer_hit()
            counter.observe(round.exposed_cards[-1])

        # ---------------------------
        # Resolve outcome
        # ---------------------------
        hand_won = False
        for hand in hand_results:
            p_best = hand.best_total
            d_best = round.dealer_hand.best_total
            if p_best is None:
                bankroll -= bet
            elif d_best is None or p_best>d_best:
                bankroll += bet
                hand_won = True
            elif p_best<d_best:
                bankroll -= bet
            else:
                pass  # push

    # ---------------------------
    # Update stats
    # ---------------------------
    session_hands += 1
    if hand_won:
        session_wins += 1
        history['wins'] += 1
    history['hands'] += 1
    save_history(history)

    # Logging
    print("Player:", render_hand(round.player_hand), "->", round.player_hand.best_total)
    print("Dealer:", render_hand(round.dealer_hand), "->", round.dealer_hand.best_total)
    print(f"Hand won: {hand_won}, Bankroll now: {bankroll}")
    print(f"Session win rate: {session_wins}/{session_hands} = {100*session_wins/session_hands:.2f}%")
    print(f"Historical win rate: {history['wins']}/{history['hands']} = {100*history['wins']/history['hands']:.2f}%")
