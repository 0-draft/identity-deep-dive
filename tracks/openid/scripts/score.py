#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

from _common import ROOT, iso_now, load_yaml, read_json, today_utc, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score OpenID repos and write candidates.json")
    p.add_argument("--date", help="Snapshot date in YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def points_by_threshold(value: int, rules: list[dict[str, Any]]) -> float:
    for r in rules:
        if value >= int(r["at_least"]):
            return float(r["points"])
    return 0.0


def points_by_recency(days: int, rules: list[dict[str, Any]]) -> float:
    for r in rules:
        if days <= int(r["within_days"]):
            return float(r["points"])
    return 0.0


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    state = read_json(ROOT / "data" / "normalized" / "state.json")
    cfg = load_yaml(ROOT / "config" / "scoring.yaml")

    recency_rules = cfg.get("recency_points", [])
    threshold_rules = cfg.get("threshold_points", {})
    weights = cfg.get("weights", {})
    settings = cfg.get("settings", {})

    top_n = int(settings.get("top_n", 12))
    deep_dive_threshold = float(settings.get("deep_dive_threshold", 8.0))
    watchlist_bonus = float(weights.get("watchlist_bonus", 0.0))
    archived_penalty = float(weights.get("archived_penalty", 0.0))

    scored: list[dict[str, Any]] = []
    for r in state.get("github_repos", []):
        recency = points_by_recency(int(r.get("days_since_push") or 99999), recency_rules)
        p_open_prs = points_by_threshold(int(r.get("open_prs", 0)), threshold_rules.get("open_prs", []))
        p_open_issues = points_by_threshold(
            int(r.get("open_issues", 0)), threshold_rules.get("open_issues", [])
        )
        p_stars = points_by_threshold(int(r.get("stars", 0)), threshold_rules.get("stars", []))
        p_merged = points_by_threshold(
            int(r.get("merged_prs_30d", 0)), threshold_rules.get("merged_prs_30d", [])
        )

        base = recency + p_open_prs + p_open_issues + p_stars + p_merged
        if r.get("watchlist"):
            base += watchlist_bonus
        if r.get("archived"):
            base += archived_penalty

        weight = float(r.get("watch_weight", 1.0))
        score = round(base * weight, 2)

        scored.append(
            {
                **r,
                "score": score,
                "score_breakdown": {
                    "recency": recency,
                    "open_prs": p_open_prs,
                    "open_issues": p_open_issues,
                    "stars": p_stars,
                    "merged_prs_30d": p_merged,
                    "watchlist_bonus": watchlist_bonus if r.get("watchlist") else 0.0,
                    "archived_penalty": archived_penalty if r.get("archived") else 0.0,
                    "weight": weight,
                    "base": round(base, 2),
                },
            }
        )

    scored.sort(
        key=lambda x: (-x["score"], x.get("days_since_push") or 99999, x["full_name"])
    )
    for i, r in enumerate(scored, start=1):
        r["rank"] = i

    candidates = {
        "generated_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "settings": {"top_n": top_n, "deep_dive_threshold": deep_dive_threshold},
        "candidates": scored,
    }

    write_json(ROOT / "data" / "normalized" / "candidates.json", candidates)
    snapshot_path = (
        ROOT / "data" / "snapshots" / snapshot_date.isoformat() / "candidates.json"
    )
    write_json(snapshot_path, candidates)

    above_threshold = sum(1 for r in scored if r["score"] >= deep_dive_threshold)
    print(
        f"score: repos={len(scored)} "
        f"top_n={top_n} "
        f"above_threshold={above_threshold}"
    )


if __name__ == "__main__":
    main()
