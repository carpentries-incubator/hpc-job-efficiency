#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def runtime(serialtime, p, N):
    return (1.0-p)*serialtime + serialtime * p/N

def speedup(x, p):
    return 1.0/(1-p+p/x)

if __name__ == "__main__":
    with plt.xkcd():
        fig,ax = plt.subplots(figsize=(10,5.625))

        X = [2**i for i in range(8)]
        Y = [runtime(100, 1, N) for N in X]
        ax.set_xticks(X)
        ax.set_xscale('log', base=2)
        plt.xlabel('Number of parallel processes')
        plt.ylabel('Execution time')

        plt.plot(X, Y)

        fig.savefig("sketch_scaling.svg")
        plt.show()
