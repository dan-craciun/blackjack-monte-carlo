import random

import matplotlib.pyplot as plt
import numpy as np

from blackjack.simulate import simulate

def main():
    random.seed(42)   # same seed so that we are working with the same random numbers
    start = 100       # we don't want to plot the first 100 hands as the running means are more volatile
    profits = np.array(simulate(1_000_000)) 
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
    fig.savefig("results/convergence.png", dpi=150, bbox_inches="tight")
    ax.legend()
    plt.show()

if __name__ == "__main__":
    main()