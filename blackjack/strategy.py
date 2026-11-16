from blackjack.cards import hand_value


# Columns (dealer upcard):  2 3 4 5 6 7 8 9 10 11(A)
# H = hit, S = stand, P = split
# D = double, if not allowed then hit
# d = double, if not allowed then stand
# Rules: 6 decks, dealer stands on soft 17, double after split allowed, no surrender

# Blackjack books
# If hand value <= 8, then it's a hit no matter what, hence not in the table
# Also, if hand is hard and hand value >= 17, it's a stand, hence not in table
# For soft hands, only >=19 is a stand
HARD = {
    9:  "HDDDDHHHHH",
    10: "DDDDDDDDHH",
    11: "DDDDDDDDDH",
    12: "HHSSSHHHHH",
    13: "SSSSSHHHHH",
    14: "SSSSSHHHHH",
    15: "SSSSSHHHHH",
    16: "SSSSSHHHHH",
}

SOFT = {
    12: "HHHHHHHHHH",
    13: "HHHDDHHHHH",
    14: "HHHDDHHHHH",
    15: "HHDDDHHHHH",
    16: "HHDDDHHHHH",
    17: "HDDDDHHHHH",
    18: "SddddSSHHH",
}

# Key = the value of ONE card of the pair. P = split, anything else = don't split (use HARD/SOFT instead)
PAIRS = {
    2:  "PPPPPPHHHH",
    3:  "PPPPPPHHHH",
    4:  "HHHPPHHHHH",
    5:  "DDDDDDDDHH",
    6:  "PPPPPHHHHH",
    7:  "PPPPPPHHHH",
    8:  "PPPPPPPPPP",
    9:  "PPPPPSPPSS",
    10: "SSSSSSSSSS",
    11: "PPPPPPPPPP",
}

def basic_strategy(hand, upcard, can_double, can_split):
    total, is_soft = hand_value(hand)       #total will be the dictionary key, is_soft is necessary to figure out which dictionry to use
    column = upcard - 2                     #this converts dealer's hand with the index of the letter within the string that is a value of it's corresponding key in the dictionary
    if can_split and hand[0] == hand[1]:    #first we check pairs 
        decision = PAIRS[hand[0]]           #use pairs dictionary
    else:
        if total <= 8:                      
            return "hit"
        if is_soft == True:                 
            if total >= 19:
                return "stand"
            decision = SOFT[total]          #use soft dictionary
        else:
            if total >= 17:
                return "stand"
            decision = HARD[total]          #use hard dictionay
    decision = decision[column]             #decision becomes its' key's value at index column
    if decision == "H":
        return "hit"
    if decision == "D":
        if can_double:
            return "double"
        return "hit"
    if decision == "S":
        return "stand"
    if decision == "d":
        if can_double:
            return "double"
        return "stand"
    if decision == "P":
        return "split"

