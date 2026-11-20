#!/usr/bin/env python3

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path


PROCESS_COUNTS = [1, 2, 4, 8]

DOMAIN_WIDTH = 8.0
LOCAL_WIDTH = 1.0
BLOCK_HEIGHT = 0.55
ROW_SPACING = 0.85

OUTPUT = Path("scaling_problem_diagram")


def draw_domain(ax, x, y, width, height, nprocs, color):
    block_width = width / nprocs
    for rank in range(nprocs):
        rect = FancyBboxPatch((x + rank * block_width, y), block_width,
                                  height, boxstyle="round,pad=0.005,rounding_size=0.025",
                                  facecolor=color, edgecolor="black", linewidth=2.0,
                                  alpha=0.35)
        ax.add_patch(rect)
        ax.text(x + (rank + 0.5) * block_width, y + height / 2,
                f"P{rank}", ha="center", va="center", fontsize=10,
                weight="bold")


def draw_strong_scaling(ax):
    ax.set_title("STRONG SCALING", fontsize=17, weight="bold", pad=15)
    ax.text(4, 4.15, "Fixed global workload; decreasing work per process",
            ha="center",fontsize=12)
    for i, nprocs in enumerate(PROCESS_COUNTS):
        y = 3.3 - i * ROW_SPACING
        draw_domain(ax, 0, y, DOMAIN_WIDTH, BLOCK_HEIGHT, nprocs, "cornflowerblue")
        ax.text(-0.35, y + BLOCK_HEIGHT / 2, f"{nprocs}P", ha="right", va="center",
                fontsize=11)
    ax.annotate("More processes", xy=(7.7, 0.7), xytext=(4.5, 0.0),
                    arrowprops=dict(arrowstyle="->", linewidth=1.8), fontsize=11,
                    ha="center")
    ax.text(4, -0.5, "Same global workload, smaller workload per process",
            ha="center", fontsize=10, weight="bold")
    ax.set_xlim(-1.3, 9)
    ax.set_ylim(-0.8, 4.7)
    ax.axis("off")


def draw_weak_scaling(ax):
    ax.set_title("WEAK SCALING", fontsize=17, weight="bold", pad=15)
    ax.text(4, 4.15, "Fixed work per process; increasing global workload",
            ha="center", fontsize=12)
    for i, nprocs in enumerate(PROCESS_COUNTS):
        y = 3.3 - i * ROW_SPACING
        draw_domain(ax, 0, y, LOCAL_WIDTH * nprocs, BLOCK_HEIGHT, nprocs,
                        "mediumseagreen")
        ax.text(-0.35, y + BLOCK_HEIGHT / 2, f"{nprocs}P", ha="right", va="center",
                fontsize=11)
    ax.annotate("More processes", xy=(7.7, 0.7), xytext=(4.5, 0.0),
                    arrowprops=dict(arrowstyle="->", linewidth=1.8), fontsize=11,
                    ha="center")
    ax.text(4, -0.5, "Same workload per process, larger global workload", ha="center",
                fontsize=10, weight="bold")
    ax.set_xlim(-1.3, 9)
    ax.set_ylim(-0.8, 4.7)
    ax.axis("off")


def main():
    with plt.xkcd(scale=1.2, length=100, randomness=2):
        fig, axes = plt.subplots(2, 1, figsize=(10, 14))
        draw_strong_scaling(axes[0])
        draw_weak_scaling(axes[1])
        fig.suptitle("Understanding Parallel Scaling", fontsize=21, weight="bold",
                        y=0.97)
        fig.text(0.5, 0.025, "Each block represents an equal computational subdomain assigned to one MPI process.",
                    ha="center", fontsize=11)
        fig.tight_layout(rect=[0, 0.06, 1, 0.91])
        for extension in ("png", "svg"):
            output = OUTPUT.with_suffix(f".{extension}")
            fig.savefig(output, dpi=300 if extension == "png" else None, bbox_inches="tight")
            print(f"Generated: {output.resolve()}")
        plt.close(fig)


if __name__ == "__main__":
    main()
