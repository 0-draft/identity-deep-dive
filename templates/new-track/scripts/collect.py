#!/usr/bin/env python3
"""Collect raw signals from configured sources.

Replace `collect_github` (or add other collectors) to match this track's
data sources. Each collector should write its raw payload under
data/raw/<YYYY-MM-DD>/<source>.json via raw_output_path() and a
normalized copy under data/normalized/<source>.json that downstream
normalize.py can merge into state.json.
"""
from __future__ import annotations

from _common import (
    ROOT,
    fetch_json,
    iso_now,
    load_sources,
    raw_output_path,
    write_json,
)


def collect_github(cfg: dict) -> dict:
    api = cfg["api_base"].rstrip("/")
    repos_out = []
    for entry in cfg.get("repos", []):
        full_name = entry["repo"]
        meta = fetch_json(f"{api}/repos/{full_name}")
        repos_out.append(
            {
                "repo": full_name,
                "pushed_at": meta.get("pushed_at", ""),
                "open_issues_count": meta.get("open_issues_count", 0),
                "stargazers_count": meta.get("stargazers_count", 0),
                "weight": entry.get("weight", 1.0),
                "category": entry.get("category"),
                "note": entry.get("note"),
            }
        )
    return {
        "collected_at": iso_now(),
        "source": "github",
        "repos": repos_out,
    }


def main() -> None:
    cfg = load_sources(ROOT / "config" / "sources.yaml")
    if "github" in cfg:
        payload = collect_github(cfg["github"])
        write_json(raw_output_path("github"), payload)
        write_json(ROOT / "data" / "normalized" / "github.json", payload)
        print(f"github: {len(cfg['github'].get('repos', []))} repos")


if __name__ == "__main__":
    main()
