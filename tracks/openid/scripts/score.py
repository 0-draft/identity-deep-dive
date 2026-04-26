#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import load_yaml, read_json, utc_now_iso, utc_today, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score normalized OpenID repository data")
    p.add_argument("--date", help="Snapshot date in YYYY-MM-DD (default: UTC today)")
    p.add_argument("--in-root", default="data/normalized")
    p.add_argument("--scoring", default="config/scoring.yaml")
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
    snapshot_date = args.date or utc_today().isoformat()

    in_file = Path(args.in_root) / f"repos-{snapshot_date}.json"
    cfg = load_yaml(Path(args.scoring))
    data = read_json(in_file)

    recency_rules = cfg.get("recency_points", [])
    threshold_rules = cfg.get("threshold_points", {})
    weights = cfg.get("weights", {})
    settings = cfg.get("settings", {})

    top_n = int(settings.get("top_n", 12))
    deep_dive_threshold = float(settings.get("deep_dive_threshold", 8.0))

    watchlist_bonus = float(weights.get("watchlist_bonus", 0.0))
    archived_penalty = float(weights.get("archived_penalty", 0.0))

    scored = []
    for r in data.get("repos", []):
        recency = points_by_recency(int(r.get("days_since_push", 99999)), recency_rules)
        p_open_prs = points_by_threshold(int(r.get("open_prs", 0)), threshold_rules.get("open_prs", []))
        p_open_issues = points_by_threshold(int(r.get("open_issues", 0)), threshold_rules.get("open_issues", []))
        p_stars = points_by_threshold(int(r.get("stars", 0)), threshold_rules.get("stars", []))
        p_merged = points_by_threshold(int(r.get("merged_prs_30d", 0)), threshold_rules.get("merged_prs_30d", []))

        base = recency + p_open_prs + p_open_issues + p_stars + p_merged
        if r.get("watchlist", False):
            base += watchlist_bonus
        if r.get("archived", False):
            base += archived_penalty

        weight = float(r.get("watch_weight", 1.0))
        score = round(base * weight, 2)

        enriched = dict(r)
        enriched["score"] = score
        enriched["score_breakdown"] = {
            "recency": recency,
            "open_prs": p_open_prs,
            "open_issues": p_open_issues,
            "stars": p_stars,
            "merged_prs_30d": p_merged,
            "watchlist_bonus": watchlist_bonus if r.get("watchlist", False) else 0.0,
            "archived_penalty": archived_penalty if r.get("archived", False) else 0.0,
            "weight": weight,
            "base": round(base, 2),
        }
        scored.append(enriched)

    scored.sort(key=lambda x: (-x["score"], x["days_since_push"], x["full_name"]))

    for i, r in enumerate(scored, start=1):
        r["rank"] = i

    out = {
        "generated_at": utc_now_iso(),
        "snapshot_date": snapshot_date,
        "source": data.get("source", {}),
        "settings": {
            "top_n": top_n,
            "deep_dive_threshold": deep_dive_threshold,
        },
        "repos": scored,
    }

    out_root = Path(args.in_root)
    out_file = out_root / f"scored-{snapshot_date}.json"
    top_file = out_root / f"top-{snapshot_date}.json"

    write_json(out_file, out)
    write_json(top_file, {**out, "repos": scored[:top_n]})

    print(f"Scored snapshot: {snapshot_date}")
    print(f"Output: {out_file}")


if __name__ == "__main__":
    main()
