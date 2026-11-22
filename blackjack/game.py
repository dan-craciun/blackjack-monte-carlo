from blackjack.cards import hand_value
from blackjack.strategy import basic_strategy


def play_round(shoe):
# first I must generate the 2 hands
    player_hand = []
    dealer_hand = []
    split_hand = []
    player_hand.append(shoe.pop())
    dealer_hand.append(shoe.pop())
    player_hand.append(shoe.pop())
    dealer_hand.append(shoe.pop())
    bet_multiplier = 1 # for double and split
    split_bet_multiplier = 0 # for doubling a split hand
    from_split = False # this is necessary for settle function. if we have a split, then we can't have blackjacks and we must consider this
# a blackjack (either side) ends the round immediately, before anyone acts. so I start by looking for blackjacks
    if is_blackjack(player_hand) and is_blackjack(dealer_hand):
        return 0
    if is_blackjack(player_hand):
        return 1.5
    if is_blackjack(dealer_hand):
        return -1
    decision = basic_strategy(player_hand, dealer_hand[0], can_double(player_hand, False), can_split(player_hand, False))
    if decision == "split":
        from_split = True
        split_bet_multiplier = 1
        split_hand.append(player_hand[0])
        player_hand.pop()
        player_hand.append(shoe.pop()) 
        player_hand, bet_multiplier = play_player_hand(player_hand, dealer_hand[0], shoe, True)
        split_hand.append(shoe.pop())
        split_hand, split_bet_multiplier = play_player_hand(split_hand, dealer_hand[0], shoe, True)
    else:
        player_hand, bet_multiplier = play_player_hand(player_hand, dealer_hand[0], shoe, False)
    if hand_value(player_hand)[0] <= 21 or (split_hand and hand_value(split_hand)[0] <= 21):
        dealer_hand = dealer_play(dealer_hand, shoe)
        settle_decision = settle(player_hand, dealer_hand, from_split)
        if split_hand:
            split_settle_decision = settle(split_hand, dealer_hand, True)
            return settle_decision * bet_multiplier + split_settle_decision * split_bet_multiplier
        return settle_decision * bet_multiplier
    else:
        return -1 * (bet_multiplier + split_bet_multiplier)

# this function plays a hand using basic strategy, where the hand can be a regular one or one coming from a split
def play_player_hand(hand, upcard, shoe, already_split):
    if already_split == True and hand[0] == 11:
        return hand, 1
    while True:
        decision = basic_strategy(hand, upcard, can_double(hand, already_split), False)
        if decision == "stand":         # in basic strategy, a bust is a stand too
            return hand, 1
        elif decision == "double":
            hand.append(shoe.pop())
            return hand, 2
        else:
            hand.append(shoe.pop())
        
def dealer_play(hand, shoe):
    total, _ = hand_value(hand)
    while total < 17:
        hand.append(shoe.pop())
        total, _ = hand_value(hand)
    return hand

def is_blackjack(hand):
    total, _ = hand_value(hand)
    if total == 21 and len(hand) == 2:
        return True
    return False

def settle(player_hand, dealer_hand, from_split = False):
    player_total, _ = hand_value(player_hand)
    dealer_total, _ = hand_value(dealer_hand)
    if player_total > 21:
        return -1
    if is_blackjack(player_hand) and not is_blackjack(dealer_hand) and not from_split:
        return 1.5
    if is_blackjack(player_hand) and is_blackjack(dealer_hand) and not from_split:
        return 0
    if is_blackjack(dealer_hand):
        return -1
    if player_total == dealer_total:
        return 0
    if dealer_total > 21 or player_total > dealer_total:
        return 1
    return -1

def can_split(hand, already_split):
    if len(hand) == 2 and hand[0] == hand[1] and not already_split:
        return True
    return False

def can_double(hand, already_split):
    if len(hand) == 2 and (not already_split or hand[0] != 11):
        """Assumes a split hand starts with the original split card at index 0."""
        return True
    return False