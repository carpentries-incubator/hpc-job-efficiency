#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import ScalarFormatter, MultipleLocator

plt.rcParams.update({
                    "font.family": "sans-serif",
                    "font.size": 8,})


def parse_arguments():
    parser = argparse.ArgumentParser(description="Create strong and weak scaling plots.")
    scaling = parser.add_mutually_exclusive_group()
    scaling.add_argument("-s", "--strong", action="store_true",
                        help="Perform strong scaling analysis.")
    scaling.add_argument("-w", "--weak", action="store_true",
                        help="Perform weak scaling analysis.")
    parser.add_argument("-i", "--input", type=Path,
                        help="Input CSV file (default: strong.csv or weak.csv,\
                              depending on the selected scaling type).")
    parser.add_argument("-o", "--output", type=Path,
                        help="Output PNG file (default: strong.png or weak.png,\
                              depending on the selected scaling type).")
    parser.add_argument("-log", "--logscale", action="store_true",
                        help="Use base-2 logarithmic scaling on x- and y-axis.")
    return parser.parse_args()


def validate_output(outputfile):
    if outputfile.suffix.lower() != ".png":
        raise ValueError(f"Output file must have a .png extension: {outputfile}")
    if outputfile.exists() and outputfile.is_dir():
        raise ValueError(f"Output path must be a file, not a directory: {outputfile}")


def load_file(filename):
    if not filename.is_file():
        raise FileNotFoundError(f"Input CSV file not found: {filename}")
    df = pd.read_csv(filename)
    required_columns = {"ntasks", "time"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"{filename} must contain columns: ntasks,time")
    df = df[["ntasks", "time"]].copy()
    df["ntasks"] = pd.to_numeric(df["ntasks"], errors="raise")
    df["time"] = pd.to_numeric(df["time"], errors="raise")
    if df.empty:
        raise ValueError(f"{filename} contains no benchmark data.")
    if df.isnull().any().any():
        raise ValueError(f"{filename} contains missing values.")
    if not np.isfinite(df["ntasks"]).all():
        raise ValueError(f"{filename} contains non-finite values in ntasks column.")
    if not np.isfinite(df["time"]).all():
        raise ValueError(f"{filename} contains non-finite values in time column.")
    if (df["ntasks"] < 1).any():
        raise ValueError(f"{filename}: ntasks must be positive")
    if (df["ntasks"] % 1 != 0).any():
        raise ValueError(f"{filename}: ntasks must contain integers")
    if (df["time"] <= 0).any():
        raise ValueError(f"{filename}: execution times must be positive.")
    if df["ntasks"].duplicated().any():
        raise ValueError(f"{filename}: duplicate ntasks entries detected.")
    if (df["ntasks"] >= 2**63).any():
        raise ValueError(f"{filename}: ntasks exceeds the supported integer range.")
    df["ntasks"] = df["ntasks"].astype(np.int64)
    df = df.sort_values("ntasks").reset_index(drop=True)
    if df["ntasks"].iloc[0] != 1:
        raise ValueError(f"{filename}: a baseline measurement with ntasks=1 is required.")
    return df


def calculate_metrics(df, scaling_type):
    if scaling_type not in {"strong", "weak"}:
        raise ValueError(f"Invalid scaling type: {scaling_type}")
    df = df.copy()
    baseline_time = df.loc[df["ntasks"] == 1, "time"].iloc[0]
    # Speedup
    if scaling_type == "strong":
        # Fixed problem size.
        df["speedup"] = baseline_time / df["time"]
    elif scaling_type == "weak":
        # Problem size increases proportionally with the number of MPI tasks.
        df["speedup"] = (baseline_time / df["time"]) * df["ntasks"]
    
    # Parallel Efficiency
    df["efficiency"] = (df["speedup"] / df["ntasks"]) * 100.0
    
    if not np.isfinite(df[["speedup", "efficiency"]]).all().all():
        raise ValueError("Calculated speedup or efficiency contains non-finite values.")
    return df


def plot_scaling_graph(df, scaling_type, scale, output):
    print(f"Creating {scaling_type} scaling plot")
    print(df.to_string(index=False))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8), sharex=True)
    # Plotting operations
    try:
        ntasks = df["ntasks"]
        
        # Speedup
        ax1.plot(ntasks, df["speedup"], marker="o", markersize=5, linestyle="-",
                    color="orange", label="Measured speedup")

        # Parallel Efficiency
        ax2.plot(ntasks, df["efficiency"], marker="o", markersize=5, linestyle="-",
                    color="orange", label="Parallel efficiency")

        # Ideal scaling reference
        ax1.plot(ntasks, ntasks, linestyle="--", color="blue", label="Ideal speedup")
        ax1.set_title(f"{scaling_type.title()} Scaling: Speedup vs. MPI Tasks", pad=10)
        ax2.set_title(f"{scaling_type.title()} Scaling: Parallel Efficiency", pad=10)

        # Ideal efficiency reference (both scaling types)
        ax2.axhline(100.0, linestyle="--", color="blue", label="Ideal efficiency (100%)")

        ax1.margins(x=0.05)
        ax1.set_ylabel("Speedup")
        ax2.set_ylabel("Efficiency (%)")
        ax2.set_xlabel("Number of MPI Tasks")
        ax1.grid(True, linestyle=":")
        ax2.grid(True, linestyle=":")
        ax1.legend()
        ax2.legend()
        ax2.set_ylim(bottom=0)

        if scale:
            print("Using base 2 logarithmic scale")
            # Log scales, base 2
            # Speedup: logarithmic x- and y-axis
            ax1.set_xscale("log", base=2)
            ax1.set_yscale("log", base=2)
            # Efficiency: logarithmic x-axis, linear y-axis
            ax2.set_xscale("log", base=2)

        ax1.set_xticks(ntasks)
        ax2.set_xticks(ntasks)
        ax1.xaxis.set_major_formatter(ScalarFormatter())
        ax1.yaxis.set_major_formatter(ScalarFormatter())
        ax2.xaxis.set_major_formatter(ScalarFormatter())

        # Efficiency remains in ordinary percentage values
        ax2.set_ylim(0, max(110.0, (np.ceil(df["efficiency"].max() / 10.0) + 1.0) * 10.0))
        ax2.yaxis.set_major_locator(MultipleLocator(10))
        ax2.yaxis.set_major_formatter(ScalarFormatter())

        fig.tight_layout()
        # Create output directory if necessary.
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, format="png", dpi=300, bbox_inches="tight")
        print(f"PNG successfully saved: {output}")
    finally:
        plt.close(fig)


def run_analysis(scaling_type, scale, inputfile, outputfile):
    inputfile = inputfile.resolve()
    outputfile = outputfile.resolve()
    print(f"Reading input CSV: {inputfile}")
    validate_output(outputfile)
    df = load_file(inputfile)
    df = calculate_metrics(df, scaling_type)
    plot_scaling_graph(df, scaling_type, scale, outputfile)


def main():
    args = parse_arguments()
    try:
        if args.strong or args.weak:
            scaling_type = ("strong" if args.strong else "weak")
            inputfile = args.input or Path(f"{scaling_type}.csv")
            outputfile = args.output or Path(f"{scaling_type}.png")
            run_analysis(scaling_type, args.logscale, inputfile, outputfile)
        else:
            if args.input or args.output:
                raise ValueError("-i or -o require either -s or -w")
            # Default: perform both analyses
            run_analysis("strong", args.logscale, Path("strong.csv"), Path("strong.png"))
            run_analysis("weak", args.logscale, Path("weak.csv"), Path("weak.png"))
    except (FileNotFoundError, ValueError,
            pd.errors.ParserError, pd.errors.EmptyDataError,
            OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
