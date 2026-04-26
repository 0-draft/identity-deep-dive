#!/usr/bin/env python3
"""Collect raw signals from configured sources.

Replace `collect_github` (or add other collectors) to match this track's
data sources. Each collector should write its raw payload under
data/raw/<YYYY-MM-DD>/<source>.json via raw_output_path().
"""
from __future__ import annotations

from _common import ROOT, fetch_json, iso_now, load_yaml, raw_output_path, write_json


def collect_github(cfg: dict) -> dict:
    api = cfg["api_base"].rstrip("/")
    repos_out = []
    for full_name in cfg.get("repos", []):
        meta = fetch_json(f"{api}/repos/{full_name}")
        repos_out.append(
            {
                "repo": full_name,
                "pushed_at": meta.get("pushed_at", ""),
                "open_issues_count": meta.get("open_issues_count", 0),
                "stargazers_count": meta.get("stargazers_count", 0),
            }
        )
    return {
        "collected_at": iso_now(),
        "source": "github",
        "repos": repos_out,
    }


def main() -> None:
    cfg = load_yaml(ROOT / "config" / "sources.yaml")
    if "github" in cfg:
        write_json(raw_output_path("github"), collect_github(cfg["github"]))
        print(f"github: {len(cfg['github'].get('repos', []))} repos")


if __name__ == "__main__":
    main()
