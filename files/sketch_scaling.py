#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def runtime(serialtime, p, N):
    return (1.0-p)*serialtime + serialtime * p/N

def speedup(serialtime, p, N):
    return 1.0/(1-p+p/N)

def efficiency(serialtime, p, N):
    return speedup(serialtime, p, N)*1.0/N

def plot(func, xlabel, ylabel, filename, ylim=None, logx=False):
    with plt.xkcd():
        fig,ax = plt.subplots(figsize=(10,5.625))

        X = [2**i for i in range(8)]
        Y  = [func(100, 1, N) for N in X]
        Y2 = [func(100, 0.98, N) for N in X]
        ax.set_xticks(X)

        if logx:
            ax.set_xscale('log', base=2)

        if ylim is not None:
            plt.ylim(ylim)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.plot(X, Y, label="100% parallelized")
        plt.plot(X, Y2, label="98% parallelized")

        plt.legend()

        fig.savefig(filename)
        plt.show()

if __name__ == "__main__":
    plot( func=runtime,
          xlabel="Number of parallel processes",
          ylabel="Execution time",
          filename="sketch_scaling.svg"
          )

    plot( func=speedup,
          xlabel="Number of parallel processes",
          ylabel="Speedup",
          filename="sketch_speedup.svg"
          )

    plot( func=efficiency,
          xlabel="Number of parallel processes",
          ylabel="Efficiency",
          filename="sketch_efficiency.svg",
          ylim=(0.0,1.05)
          )
