#!/usr/bin/env python3
"""Dispatcher for daily/weekly report generation."""
import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render OpenID report",
        add_help=False,
    )
    parser.add_argument("--mode", choices=["daily", "weekly"], required=True)
    args, rest = parser.parse_known_args()

    sys.argv = [sys.argv[0], *rest]
    if args.mode == "daily":
        from generate_daily_report import main as run
    else:
        from generate_weekly_report import main as run
    run()


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    main()
