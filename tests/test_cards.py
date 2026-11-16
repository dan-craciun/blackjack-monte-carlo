from blackjack.cards import build_shoe, hand_value

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

            