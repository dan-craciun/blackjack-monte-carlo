import random   

import pandas as pd
import numpy as np

from blackjack.simulate import simulate
from blackjack.betsize import flat, spread, full_kelly, half_kelly, bankroll_path

STRATEGIES = {
    "Flat": flat,
    "Spread 1-8": spread,
    "Full Kelly": full_kelly,
    "Half Kelly": half_kelly,
}

def run_paths(true_counts, profits, strategies, n_paths, n_rounds, start_bankroll):
    # Split the simulated rounds into n_paths sessions of n_rounds each and run
    # every strategy on every session. Returns a DataFrame with one row per
    # (strategy, path): final bankroll and whether the path was ruined."""
    rows = []
    for i in range(n_paths):
        start = i * n_rounds
        end = (i + 1) * n_rounds
        counts_i = true_counts[start:end]
        profits_i = profits[start:end]
        for name, rule in strategies.items():
            path = bankroll_path(counts_i, profits_i, rule, start_bankroll)
            rows.append({                # creates list of dictionaries that gets transformed in a data frame
                "strategy": name,
                "path": i,
                "final": path[-1],
                "ruined": path[-1] < 1,
            })
    return pd.DataFrame(rows)

def summarize_strategies(results):
    # Summarises the results per strategy: risk of ruin and the distribution of final bankrolls
    summary = results.groupby("strategy").agg(
        risk_of_ruin=("ruined", "mean"), # ruin = true = 1, ruin = false = 0, mean of 1's and 0's will give the % chance of ruin 
        mean_final=("final", "mean"),
        median_final=("final", "median"),
        p5_final=("final", lambda x: x.quantile(0.05)),     # 5th percentile using a lambda function
        p95_final=("final", lambda x: x.quantile(0.95)),    # 95th percentile
        std_final=("final", "std"),
        n_paths=("final", "count"),
    )
    summary["se_mean"] = summary["std_final"] / np.sqrt(summary["n_paths"])
    summary["ci_low"] = summary["mean_final"] - 1.96 * summary["se_mean"]
    summary["ci_high"] = summary["mean_final"] + 1.96 * summary["se_mean"]
    return summary

def main():
    pd.set_option("display.max_rows", None)      # show every row of summary 
    pd.set_option("display.max_columns", None)   # show every column of summary 
    pd.set_option("display.width", None)         # use the full terminal width, no wrapping
    random.seed(42)
    n_paths = 200    # 200 different players
    n_rounds = 10_000 # playing 10k rounds each
    start_bankroll = 1_000

    true_counts, profits = simulate(n_paths * n_rounds)
    results = run_paths(true_counts, profits, STRATEGIES, n_paths, n_rounds, start_bankroll)
    summary = summarize_strategies(results)
    print(summary)

if __name__ == "__main__":
    main()