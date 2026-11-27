# Fitted in analysis.py (weighted least squares, 2M rounds, seed 42)
EDGE_INTERCEPT = -0.00516
EDGE_SLOPE = 0.00485

# Variance of one round's profit (std ≈ 1.1466 from simulate.py)
VARIANCE = 1.1466 ** 2

def flat(tc, bankroll):
    return 1

def spread(tc, bankroll):
    if tc < 2: 
        return 1
    if tc < 3:
        return 2
    if tc < 4:
        return 4
    if tc < 5:
        return 6
    return 8

def edge(tc):
    # Estimated player edge at true count tc
    return EDGE_INTERCEPT + EDGE_SLOPE * tc

def kelly_bet(tc, bankroll, fraction):
    curr_edge = edge(tc)
    if curr_edge <= 0:
        return 1
    return max(1, fraction * bankroll * curr_edge / VARIANCE)

def full_kelly(tc, bankroll):
    return kelly_bet(tc, bankroll, 1)

def half_kelly(tc, bankroll):
    return kelly_bet(tc, bankroll, 0.5)

def bankroll_path(true_counts, profits, bet_rule, start_bankroll):
    bankroll = start_bankroll
    path = [start_bankroll]
    for tc, profit in zip(true_counts, profits):
        bet = min(bet_rule(tc, bankroll), bankroll)
        bankroll = max(bankroll + bet * profit, 0)
        path.append(bankroll)
        if bankroll < 1:
            break
    return path