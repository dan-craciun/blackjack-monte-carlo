def hilo_value(card):                    # this tells us whether the card is +1, 0, or -1
    if 2 <= card <= 6:
        return 1
    elif 7 <= card <= 9:
        return 0
    else:
        return -1 

def true_count(shoe):
    count = 0
    for card in shoe:
        count += hilo_value(card)        # count of cards left in shoe. running count + this count = 0 so running count = - this count
    return -count * 52 / len(shoe)       # the true count is = running count / no of decks left

