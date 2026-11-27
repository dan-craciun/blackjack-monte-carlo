import random

import pandas as pd
import pytest

from blackjack.analysis import edge_by_count, fit_edge
from blackjack.betsize import (
    EDGE_INTERCEPT,
    bankroll_path,
    edge,
    flat,
    full_kelly,
    half_kelly,
    kelly_bet,
    spread,
)
from blackjack.cards import build_shoe, hand_value
from blackjack.compare_strategies import run_paths, summarize_strategies
from blackjack.counting import hilo_value, true_count
from blackjack.game import (
    can_double,
    can_split,
    dealer_play,
    is_blackjack,
    play_player_hand,
    play_round,
    settle,
)
from blackjack.simulate import simulate, summarize
from blackjack.strategy import basic_strategy


# Rigged shoes are read from right to left: pop() takes the last card first.


# ---------- cards.py ----------

def test_hand_value_soft():
    assert hand_value([11, 7]) == (18, True)
    assert hand_value([11, 11, 8]) == (20, True)
    assert hand_value([11, 10]) == (21, True)
    assert hand_value([11, 11, 11, 11, 7]) == (21, True)


def test_hand_value_hard():
    assert hand_value([6, 9]) == (15, False)
    assert hand_value([10, 10, 11]) == (21, False)
    assert hand_value([11, 11, 10]) == (12, False)


def test_hand_value_bust():
    assert hand_value([10, 5, 8]) == (23, False)
    assert hand_value([11, 10, 10, 5]) == (26, False)


def test_build_shoe():
    shoe = build_shoe(1)
    assert len(shoe) == 52
    assert sum(shoe) == 380
    shoe = build_shoe(6)
    assert len(shoe) == 312
    assert sum(shoe) == 2280


# ---------- game.py ----------

def test_dealer_play():
    assert dealer_play([11, 6], [2, 10, 8, 9]) == [11, 6]            # stands on soft 17
    assert dealer_play([5, 5, 6], [10, 10]) == [5, 5, 6, 10]         # busts
    assert dealer_play([11, 10], [11, 3, 4, 5]) == [11, 10]          # already 21
    assert dealer_play([2, 3], [8, 4, 4]) == [2, 3, 4, 4, 8]         # several draws
    assert dealer_play([11, 5], [4, 10]) == [11, 5, 10, 4]           # soft 16 turns hard, keeps drawing


def test_dealer_play_removes_cards_from_shoe():
    shoe = [5, 3]
    dealer_play([10, 2], shoe)
    assert shoe == []


def test_is_blackjack():
    assert is_blackjack([10, 11]) is True
    assert is_blackjack([5, 6, 10]) is False
    assert is_blackjack([9, 10]) is False


def test_settle():
    assert settle([11, 10], [10, 11]) == 0          # both blackjack
    assert settle([11, 10], [10, 8]) == 1.5         # player blackjack
    assert settle([5, 6, 10], [11, 10]) == -1       # dealer blackjack beats 3-card 21
    assert settle([9, 7], [10, 6, 7]) == 1          # dealer busts
    assert settle([10, 6, 9], [10, 6, 10]) == -1    # both bust: player loses
    assert settle([10, 7], [10, 7]) == 0            # push
    assert settle([10, 7], [10, 9]) == -1           # normal loss


def test_settle_split_21_is_not_blackjack():
    assert settle([11, 10], [10, 8], from_split=True) == 1
    assert settle([11, 10], [10, 5, 6], from_split=True) == 0


def test_can_split():
    assert can_split([8, 8], False) is True
    assert can_split([8, 8], True) is False         # no re-splitting
    assert can_split([8, 9], False) is False
    assert can_split([8, 8, 2], False) is False


def test_can_double():
    assert can_double([6, 5], False) is True
    assert can_double([6, 3, 2], False) is False    # only on two cards
    assert can_double([6, 5], True) is True         # double after split allowed
    assert can_double([11, 5], True) is False       # but not on split aces


def test_play_player_hand():
    assert play_player_hand([6, 5], 6, [10], False) == ([6, 5, 10], 2)       # double
    assert play_player_hand([10, 6], 10, [2, 5], False) == ([10, 6, 5], 1)   # hit to 21, stand
    assert play_player_hand([11, 7], 10, [9], True) == ([11, 7], 1)          # split aces: no more cards


def test_play_round():
    assert play_round([7, 10, 9, 11]) == 1.5                   # player blackjack
    assert play_round([10, 10, 7, 6, 10]) == 1                 # stand on 17, dealer busts
    assert play_round([2, 10, 10, 5, 6, 6]) == 2               # double and win
    assert play_round([9, 10, 8, 11, 10, 11]) == 2             # split aces: A+10 pays 1, not 1.5


def test_play_round_dealer_does_not_draw_after_player_busts():
    shoe = [5, 10, 7, 6, 10, 10]
    assert play_round(shoe) == -1
    assert shoe == [5]


# ---------- strategy.py ----------

def test_basic_strategy_hard():
    assert basic_strategy([10, 6], 10, True, False) == "hit"
    assert basic_strategy([10, 6], 6, True, False) == "stand"
    assert basic_strategy([10, 8], 6, True, False) == "stand"
    assert basic_strategy([5, 3], 6, True, False) == "hit"
    assert basic_strategy([3, 8], 10, True, False) == "double"


def test_basic_strategy_soft():
    assert basic_strategy([11, 6], 7, True, False) == "hit"
    assert basic_strategy([11, 6], 4, True, False) == "double"
    assert basic_strategy([11, 8], 6, True, False) == "stand"


def test_basic_strategy_double_fallback():
    assert basic_strategy([6, 5], 6, False, False) == "hit"     # D without double → hit
    assert basic_strategy([7, 11], 3, False, False) == "stand"  # d without double → stand


def test_basic_strategy_pairs():
    assert basic_strategy([11, 11], 8, True, True) == "split"
    assert basic_strategy([8, 8], 10, True, True) == "split"
    assert basic_strategy([8, 8], 10, True, False) == "hit"     # can't split → hard 16
    assert basic_strategy([5, 5], 6, True, True) == "double"    # never split 5s


# ---------- counting.py ----------

def test_hilo_value():
    assert [hilo_value(c) for c in range(2, 12)] == [1, 1, 1, 1, 1, 0, 0, 0, -1, -1]


def test_true_count():
    assert true_count(build_shoe(6)) == 0
    assert true_count([10] * 52) == 52
    assert true_count([2] * 26) == -52


# ---------- betsize.py ----------

def test_flat():
    assert flat(5, 1000) == 1


def test_spread():
    assert spread(-3, 1000) == 1
    assert spread(1.99, 1000) == 1
    assert spread(2.37, 1000) == 2
    assert spread(3.5, 1000) == 4
    assert spread(4.9, 1000) == 6
    assert spread(7, 1000) == 8


def test_edge():
    assert edge(0) == EDGE_INTERCEPT


def test_kelly():
    assert kelly_bet(-2, 1000, 1) == 1                          # negative edge: table minimum
    assert kelly_bet(4, 1000, 1) == pytest.approx(10.83, abs=0.01)
    assert full_kelly(4, 1000) == pytest.approx(10.83, abs=0.01)
    assert half_kelly(4, 1000) == pytest.approx(5.42, abs=0.01)
    assert kelly_bet(2, 100, 1) == 1                            # Kelly bet below minimum


def test_bankroll_path():
    assert bankroll_path([0, 3, 0], [1, -1, 1], spread, 10) == [10, 11, 7, 8]
    assert bankroll_path([5, 5], [-1, -1], spread, 10) == [10, 2, 0]     # ruin stops the path
    assert bankroll_path([0], [-2], flat, 1) == [1, 0]                   # can't go below zero


# ---------- simulate.py ----------

def test_summarize():
    mean, std, se, ci_low, ci_high = summarize([1, -1, 1, -1])
    assert mean == 0
    assert ci_low < 0 < ci_high


def test_simulate_is_reproducible():
    random.seed(1)
    first = simulate(200)
    random.seed(1)
    second = simulate(200)
    assert first == second
    assert len(first[0]) == len(first[1]) == 200


# ---------- analysis.py ----------

def test_edge_by_count():
    table = edge_by_count([0.2, 0.7, 1.5], [1, -1, 2], min_rounds=1)
    assert list(table.index) == [0, 1]
    assert table.loc[0, "count"] == 2
    assert table.loc[0, "mean"] == 0
    assert table.loc[0, "avg_tc"] == pytest.approx(0.45)
    assert table.loc[1, "mean"] == 2


def test_edge_by_count_filters_small_buckets():
    table = edge_by_count([0.2, 0.7, 1.5], [1, -1, 2], min_rounds=2)
    assert list(table.index) == [0]


def test_fit_edge():
    table = pd.DataFrame({"avg_tc": [0, 1, 2], "mean": [0.1, 0.3, 0.5], "se": [1, 1, 1]})
    slope, intercept = fit_edge(table)
    assert slope == pytest.approx(0.2)
    assert intercept == pytest.approx(0.1)


# ---------- compare_strategies.py ----------

def test_run_paths():
    results = run_paths([0, 0, 0, 0], [1, 1, -1, -1], {"Flat": flat},
                        n_paths=2, n_rounds=2, start_bankroll=10)
    assert list(results["final"]) == [12, 8]
    assert not results["ruined"].any()


def test_summarize_strategies():
    results = pd.DataFrame({
        "strategy": ["A", "A", "A", "A"],
        "path": [0, 1, 2, 3],
        "final": [0, 50, 100, 150],
        "ruined": [True, False, False, False],
    })
    summary = summarize_strategies(results)
    assert summary.loc["A", "risk_of_ruin"] == 0.25
    assert summary.loc["A", "mean_final"] == 75