import random

import numpy as np

from blackjack.cards import build_shoe
from blackjack.game import play_round
from blackjack.counting import true_count

def simulate(n_rounds, n_decks = 6, penetration = 0.75):
    """Play n_rounds of blackjack and return a list of each round's profit and true count."""
    # 6 decks contain 6 * 52 = 312 cards
    # so penetration = 75% is reached when we reach 312 * 0.75 = 234 cards, that means when there are 312 - 234 = 78 cards left
    # so shoe gets reshuffled when len(shoe) < n_decks * 52 * (1 - penetration)
    shoe = build_shoe(n_decks)
    profit_list = []
    true_counts = []
    reshuffle_at = n_decks * 52 * (1 - penetration)
    for _ in range(n_rounds):
        if len(shoe) < reshuffle_at:
            shoe = build_shoe(n_decks)
        true_counts.append(true_count(shoe))
        profit_list.append(play_round(shoe))
    return true_counts, profit_list

def summarize(profits):
    """Return mean, std, standard error and 95% CI of the profits."""
    profits = np.array(profits) 
    mean = profits.mean()  # mean
    std = profits.std(ddof=1) # standard deviation 
    se = std / np.sqrt(len(profits)) # standard error
    ci_low = mean - 1.96 * se    # lower end of the 95% confidence interval
    ci_high = mean + 1.96 * se   # upper end of the 95% confidence interval
    return mean, std, se, ci_low, ci_high

def main():
    random.seed(42) # added a seed so that anyone can rerun the code and get the same results
    _, profits = simulate(10_000_000)
    mean, std, se, ci_low, ci_high = summarize(profits)
    print(f"Mean profit per round:  {mean:.4f}")
    print(f"House edge:             {-mean:.2%}")
    print(f"Standard deviation:     {std:.4f}")
    print(f"Standard error:         {se:.5f}")
    print(f"95% CI:                 [{ci_low:.4f}, {ci_high:.4f}]")

if __name__ == "__main__":
    main()

        
