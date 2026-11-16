from blackjack.cards import hand_value


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

def settle(player_hand, dealer_hand):
    player_total, _ = hand_value(player_hand)
    dealer_total, _ = hand_value(dealer_hand)
    if player_total > 21:
        return -1
    if is_blackjack(player_hand) and not is_blackjack(dealer_hand):
        return 1.5
    if is_blackjack(player_hand) and is_blackjack(dealer_hand):
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