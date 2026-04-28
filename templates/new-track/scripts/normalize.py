#!/usr/bin/env python3
"""Merge per-source normalized files into state.json + a daily snapshot."""
from __future__ import annotations

import argparse
import datetime as dt

from _common import ROOT, iso_now, read_json, today_utc, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build normalized state.json")
    p.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    state: dict = {
        "generated_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "sources": {},
    }

    github_path = ROOT / "data" / "normalized" / "github.json"
    if github_path.exists():
        gh = read_json(github_path)
        state["sources"]["github"] = gh.get("collected_at", "")
        state["github_repos"] = gh.get("repos", [])

    write_json(ROOT / "data" / "normalized" / "state.json", state)
    snapshot_path = (
        ROOT / "data" / "snapshots" / snapshot_date.isoformat() / "state.json"
    )
    write_json(snapshot_path, state)
    print(f"normalize: sources={list(state['sources'].keys())}")


if __name__ == "__main__":
    main()
