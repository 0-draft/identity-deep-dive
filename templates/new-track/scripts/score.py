#!/usr/bin/env python3
"""Rank items into a deep-dive candidate queue using config/scoring.yaml."""
from __future__ import annotations

import datetime as dt

from _common import ROOT, iso_now, load_yaml, read_json, write_json, write_text


def days_since(iso: str) -> int | None:
    if not iso:
        return None
    try:
        when = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    except ValueError:
        return None
    return (dt.date.today() - when).days


def main() -> None:
    state = read_json(ROOT / "data" / "normalized" / "state.json")
    cfg = load_yaml(ROOT / "config" / "scoring.yaml")

    weights = cfg.get("weights", {})
    recency = cfg.get("recency_days", {})
    threshold = int(cfg.get("thresholds", {}).get("min_candidate_score", 0))

    candidates = []
    for repo in state.get("github_repos", []):
        age = days_since(repo.get("pushed_at", ""))
        if age is None or age > int(recency.get("github_activity", 30)):
            continue
        candidates.append(
            {
                "title": f"Review repo activity: {repo.get('repo', '')}",
                "score": int(weights.get("github_activity", 1)),
                "evidence": f"pushed_at={repo.get('pushed_at', '')}",
            }
        )

    ranked = sorted(
        (c for c in candidates if c["score"] >= threshold),
        key=lambda c: -c["score"],
    )

    write_json(
        ROOT / "data" / "normalized" / "candidates.json",
        {"generated_at": iso_now(), "threshold": threshold, "candidates": ranked},
    )

    lines = ["# Candidate Queue", "", f"Generated at: {iso_now()}", "", "| Rank | Score | Candidate |", "| --- | ---: | --- |"]
    if not ranked:
        lines.append("| - | - | No candidates above threshold |")
    else:
        for i, c in enumerate(ranked, start=1):
            lines.append(f"| {i} | {c['score']} | {c['title']} |")
    write_text(ROOT / "deep-dives" / "_backlog.md", "\n".join(lines) + "\n")
    print(f"score: candidates={len(ranked)} threshold={threshold}")


if __name__ == "__main__":
    main()
