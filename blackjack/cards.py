import random


def build_shoe(number_decks):
    shoe = []
    for i in range (2, 12):
        if i == 10:
            shoe.extend([10] * 16 * number_decks)
        else:
            shoe.extend([i] * 4 * number_decks)
    random.shuffle(shoe)
    return shoe

def hand_value(hand):                                           
    is_soft = False                                          
    total_value = sum(hand)
    aces = hand.count(11)
    while total_value > 21 and aces > 0:
        total_value -= 10
        aces -= 1
    if aces > 0:
        is_soft = True
    return total_value, is_soft
