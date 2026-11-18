#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def runtime(serialtime, p, N):
    return serialtime * ((1.0 - p) + (p / N))

def speedup(serialtime, p, N):
    return 1.0 / ((1.0 - p) + (p / N))

def efficiency(serialtime, p, N):
    return (speedup(serialtime, p, N) / N) * 100.0

def plot(func, xlabel, ylabel, filename, ylim=None):
    N = 2 ** np.arange(8)
    curves = {
                "100% parallelized": func(100, 1.0, N),
                "98% parallelized": func(100, 0.98, N),
                }
    filename = Path(filename)
    # Generate both linear and logarithmic plots
    for scale in ("linear", "log2"):
        with plt.xkcd():
            fig, ax = plt.subplots(figsize=(10, 5.625))
            for label, Y in curves.items():
                ax.plot(N, Y, marker="o", label=label)
            if scale == "log2":
                ax.set_xscale('log', base=2)
            ax.set_xticks(N)
            ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
            if ylim is not None:
                ax.set_ylim(ylim)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(f"{ylabel} vs. Number of Parallel Processors")
            ax.grid(True, linestyle=":")
            ax.legend()
            fig.tight_layout()
            output = filename.with_name(f"{filename.stem}_{scale}{filename.suffix}")
            fig.savefig(output, format="svg", bbox_inches="tight")
            print(f"Plot saved: {output.resolve()}")
            plt.close(fig)

if __name__ == "__main__":
    plot(func=runtime, xlabel="Number of parallel processes",
            ylabel="Execution time", filename="sketch_scaling.svg")

    plot(func=speedup, xlabel="Number of parallel processes",
            ylabel="Speedup", filename="sketch_speedup.svg")

    plot(func=efficiency, xlabel="Number of parallel processes",
            ylabel="Efficiency (%)", filename="sketch_efficiency.svg", ylim=(0.0,105.0))
