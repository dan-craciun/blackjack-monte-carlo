import random

import matplotlib.pyplot as plt
import numpy as np

from blackjack.simulate import simulate


def plot_convergence(profits, path="results/convergence.png"):
    # Plot the running mean of profits with its 95% CI on a log x-axis.
    profits = np.array(profits)
    start = 100       # we don't want to plot the first 100 hands as the running means are more volatile
    k = np.arange(1, len(profits) + 1)        # 1, 2, 3, ..., n (x axis)
    running_mean = np.cumsum(profits) / k     # mean after each round (y axis) 
    fig, ax = plt.subplots()                  # create figure
    ax.plot(k[start:], running_mean[start:], label="Running mean")  # plot it
    ax.set_xscale("log")                      # this makes the points from the 100 - 1000 hands and 1000 - 10000 hands (and so on) evenly spaced
    s = profits.std(ddof=1)
    half_width = 1.96 * s / np.sqrt(k)
    ax.fill_between(k[start:], running_mean[start:] - half_width[start:], running_mean[start:] + half_width[start:], alpha=0.3, label ="95% CI") #this represents, through a shaded area, the 95% confidence interval
    ax.axhline(running_mean[-1], linestyle="--", color="gray", label=f"Final estimate ({running_mean[-1]:.4f})")
    ax.set_xlabel("Rounds played (log scale)")
    ax.set_ylabel("Mean profit per round (units of bet)")
    ax.set_title("Monte Carlo convergence of blackjack expected value")
    ax.legend()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_edge_by_count(table, slope, intercept, path="results/edge_by_count.png"):
    # Plot mean profit per true-count bucket with 95% CIs and the fitted line.
    fig, ax = plt.subplots()  # create fig and axes
    ax.errorbar(table["avg_tc"], table["mean"],         # one dot per bucket, with its 95% CI as a vertical bar
                yerr=1.96 * table["se"],
                fmt="o", capsize=3,
                label="Simulated edge (95% CI)")
    x = np.linspace(table["avg_tc"].min(), table["avg_tc"].max(), 100) # create 100 evenly spaced points between min relevant count and max relevant count
    ax.plot(x, intercept + slope * x, label=f"Fit: {intercept:.4f} + {slope:.4f}·TC")   # this plots edge in terms of x which is avarage tc
    ax.axhline(0, color="gray", linewidth=0.8) # line y = 0
    ax.set_xlabel("True count (Hi-Lo)")
    ax.set_ylabel("Mean profit per round (units of bet)")      # Labels
    ax.set_title("Player edge by true count")
    ax.legend()
    fig.savefig(path, dpi=150, bbox_inches="tight")   # save
    plt.show() # show


def main():
    random.seed(42)   # same seed so that we are working with the same random numbers
    _, profits = simulate(1_000_000)
    plot_convergence(profits)


if __name__ == "__main__":
    main()