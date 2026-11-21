from blackjack.cards import build_shoe, hand_value
from blackjack.game import dealer_play, is_blackjack, settle
from blackjack.strategy import basic_strategy


def test_soft_cards():
    assert hand_value([11, 7]) == (18, True)
    assert hand_value([11, 11, 8]) == (20, True)
    assert hand_value([11, 10]) == (21, True)

def test_hard_cards():
    assert hand_value([10, 5, 8]) == (23, False)
    assert hand_value([6, 9]) ==(15, False)
    assert hand_value([10, 10, 11]) ==(21, False)
    assert hand_value([11, 11, 10]) == (12, False)

def test_shoe():
    assert len(build_shoe(1)) == 52
    assert sum(build_shoe(1)) == 380 

def test_dealer_draws():                                       #remember you read shoe from right to left
    assert dealer_play([11, 6], [2, 10, 8, 9]) == [11, 6]
    assert dealer_play([5, 5, 6] , [10, 10]) == [5, 5, 6, 10]
    assert dealer_play([11, 10] , [11, 3, 4, 5]) == [11, 10]
    assert dealer_play([2, 3] , [8, 4, 4]) == [2, 3, 4, 4, 8]

def test_is_blackjack():
    assert is_blackjack([5, 6, 10]) == False
    assert is_blackjack([10, 11]) == True
    assert is_blackjack([9, 10]) == False

def test_settle():
    assert settle([11, 10], [10, 11]) == 0
    assert settle([9, 7] , [10, 6, 7]) == 1
    assert settle([5, 6, 10], [11, 10]) == -1
    assert settle([11, 10], [10, 8]) == 1.5

def test_basic_strategy():
    assert basic_strategy([11, 6], 7, True, False) == "hit"
    assert basic_strategy([11, 11], 8, True, True) == "split"
    assert basic_strategy([3, 8], 10, True, False) == "double"
    assert basic_strategy([4, 6, 5], 6, False, False) == "stand"
    assert basic_strategy([7, 11], 3, False, False) =="stand"

