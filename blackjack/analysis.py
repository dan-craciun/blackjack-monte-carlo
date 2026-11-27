import random

import pandas as pd
import numpy as np

from blackjack.simulate import simulate
from blackjack.plots import plot_edge_by_count

def edge_by_count(true_counts, profits, min_rounds=10_000):
    df = pd.DataFrame({"true_count" : true_counts, "profit" : profits}) # build a data frame with 2 columns: tc and profit
    df["tc_bucket"] = np.floor(df["true_count"]).astype(int) # this rounds down tcs 
    table = df.groupby("tc_bucket").agg(       # group by the same rounded-down tc                      
        avg_tc=("true_count", "mean"),         # this gives the avarage tc of the group
        mean=("profit", "mean"),               # this gives the avarage profit of the group
        std=("profit", "std"),                 # std of the profits within each group
        count=("profit", "count"),             # no of hands per group
    )
    # each group becomes one row in the table
    table["se"] = table["std"] / np.sqrt(table["count"])  # standard error of each group
    table["ci_low"] = table["mean"] - 1.96 * table["se"]  # CI_low of each group
    table["ci_high"] = table["mean"] + 1.96 * table["se"] # CI_high of each group
    table = table[table["count"] >= min_rounds]           # this filters out groups with too few hands, because these are very voltatile and unrepresentative
    return table

def fit_edge(table):
    slope, intercept = np.polyfit(table["avg_tc"], table["mean"], 1, w = 1 / table["se"])  # this takes all points(x,y) where x is the avg_tc of a group and y is
                                                                                           # is the mean return of the group, and gives us the slope and y-intercept 
                                                                                           # of the line that best represents the points
                                                                                           # least squares method
                                                                                           # w=1 / table["se"] is a weighted fit. Buckets with small SE (that is, with many rounds) count more than noisy ones.
    ## print (f"edge(TC) = {intercept:.5f} + {slope:.5f} * TC") # this is edge formula in terms of TC
    return slope, intercept

def main():
    random.seed(42)  # use same seed
    true_counts, profits = simulate(2_000_000)  # get profits and counts
    table = edge_by_count(true_counts, profits) # get table
    slope, intercept = fit_edge(table) # fit the line edge(TC) = intercept + slope · TC.
    print(table)
    print(f"edge(TC) = {intercept:.5f} + {slope:.5f} * TC")
    plot_edge_by_count(table, slope, intercept)

if __name__ == "__main__":
    main()