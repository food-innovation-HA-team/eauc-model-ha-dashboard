"""
cli.py

Simple command-line interface for the modelling tool.
"""

import argparse
from run_model import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Agribalyse modelling tool")
    parser.add_argument(
        "mode",
        choices=["baseline", "scenario", "multipliers"],
        help="Which pipeline to run"
    )

    args = parser.parse_args()

    if args.mode == "baseline":
        run_pipeline()

    elif args.mode == "scenario":
        run_pipeline(apply_structural_scenarios=True)

    elif args.mode == "multipliers":
        run_pipeline(apply_multiplier_scenarios=True)


if __name__ == "__main__":
    main()
