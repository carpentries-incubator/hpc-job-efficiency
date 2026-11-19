#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter, MultipleLocator


def runtime(serialtime, p, N):
    return serialtime * ((1.0 - p) + (p / N))

def speedup(serialtime, p, N):
    return 1.0 / ((1.0 - p) + (p / N))

def efficiency(serialtime, p, N):
    return (speedup(serialtime, p, N) / N) * 100.0

def plot(func, xlabel, ylabel, filename, ylim=None, log_y=False, efficiency_plot=False):
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
                if log_y and not efficiency_plot:
                    ax.set_yscale('log', base=2)
            ax.set_xticks(N)
            ax.xaxis.set_major_formatter(ScalarFormatter())
            ax.yaxis.set_major_formatter(ScalarFormatter())
            if ylim is not None:
                ax.set_ylim(ylim)
            # Kepp efficiency in ordinary percentage values:
            if efficiency_plot:
                ax.set_ylim(0, 105)
                ax.yaxis.set_major_locator(MultipleLocator(10))
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(f"{ylabel} vs. Number of Parallel Processors")
            ax.grid(True, linestyle=":", lw=1, zorder=0)
            ax.legend()
            fig.tight_layout()
            output = filename.with_name(f"{filename.stem}_{scale}{filename.suffix}")
            fig.savefig(output, format="svg", bbox_inches="tight")
            print(f"Plot saved: {output.resolve()}")
            plt.close(fig)

if __name__ == "__main__":
    plot(func=runtime, xlabel="Number of parallel processes",
            ylabel="Execution time", filename="sketch_scaling.svg", log_y=True)

    plot(func=speedup, xlabel="Number of parallel processes",
            ylabel="Speedup", filename="sketch_speedup.svg", log_y=True)

    plot(func=efficiency, xlabel="Number of parallel processes",
            ylabel="Efficiency (%)", filename="sketch_efficiency.svg", ylim=(0.0,105.0),
            efficiency_plot=True)
