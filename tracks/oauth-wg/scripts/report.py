#!/usr/bin/env python3
"""Dispatcher for daily/weekly report generation."""
import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Render OAuth WG report")
    parser.add_argument("--mode", choices=["daily", "weekly"], required=True)
    args, _ = parser.parse_known_args()

    if args.mode == "daily":
        from build_daily_report import main as run
    else:
        from build_weekly_report import main as run
    run()


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    main()
