#! /usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def strong_scaling():
    print("Creating strong scaling plot\n")

    strongdf = pd.read_csv("./strong.csv")

    # Calculate speedup
    strongdf["speedup"] = strongdf.loc[strongdf["ntasks"] == 1, "time"].values[0] / strongdf["time"]

    # Calculate efficiency
    strongdf["efficiency"] = strongdf["speedup"]/strongdf["ntasks"]

    print(strongdf)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
    strongdf.plot(x='ntasks', y='speedup', ax=ax1, title='Speedup vs. ntasks', grid=True, linestyle='none', marker='o')
    strongdf.plot(x='ntasks', y='efficiency', ax=ax2, title='Efficiency vs. ntasks', grid=True, linestyle='none', marker='o')

    ax1.axline((1, 1), slope=1, color='red', label="Ideal speedup")
    ax1.legend()

    max_speedup = strongdf['speedup'].max()
    ax1.set_xlim(0, 130)
    ax2.set_xlim(0, 130)
    ax1.set_ylim(0, 2 * max_speedup)
    ax2.set_ylim(0, 1.05)

    xticks = [4] + [ 8 * i for i in range(17) ]
    ax1.set_xticks(xticks)
    ax2.set_xticks(xticks)

    plt.tight_layout()
    plt.savefig("strong_scaling.png", dpi=300)
    plt.show()


def weak_scaling():
    print("Creating strong scaling plot\n")

    weakdf = pd.read_csv("./weak.csv")

    # Calculate speedup
    # Since workload increases with "ntasks", e.g. twice the number of pixels for 2 processes,
    # we can use it as a factor for the speedup calculation
    weakdf["speedup"] = weakdf.loc[weakdf["ntasks"] == 1, "time"].values[0] / weakdf["time"] * weakdf["ntasks"]

    # Calculate efficiency
    weakdf["efficiency"] = weakdf["speedup"]/weakdf["ntasks"]

    print(weakdf)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
    weakdf.plot(x='ntasks', y='speedup', ax=ax1, title='Speedup vs. ntasks', grid=True, linestyle='none', marker='o')
    weakdf.plot(x='ntasks', y='efficiency', ax=ax2, title='Efficiency vs. ntasks', grid=True, linestyle='none', marker='o')

    ax1.axline((1, 1), slope=1, color='red', label="Ideal speedup")
    ax1.legend()

    max_speedup = weakdf['speedup'].max()
    ax1.set_xlim(0, 65)
    ax2.set_xlim(0, 65)
    ax1.set_ylim(0, 2 * max_speedup)
    ax2.set_ylim(0, 1.05)

    xticks = [4] + [ 8 * i for i in range(9) ]
    ax1.set_xticks(xticks)
    ax2.set_xticks(xticks)

    plt.tight_layout()
    plt.savefig("weak_scaling.png", dpi=300)
    plt.show()

def main():
    strong_scaling()
    weak_scaling()

if __name__ == "__main__":
    main()
