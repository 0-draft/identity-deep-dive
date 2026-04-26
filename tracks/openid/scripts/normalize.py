#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import days_since, load_yaml, read_json, utc_now_iso, utc_today, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalize raw OpenID data")
    p.add_argument("--date", help="Snapshot date in YYYY-MM-DD (default: UTC today)")
    p.add_argument("--raw-root", default="data/raw")
    p.add_argument("--out-root", default="data/normalized")
    p.add_argument("--watchlist", default="config/watchlist.yaml")
    return p.parse_args()


def classify(name: str) -> str:
    if name.startswith("AppAuth-"):
        return "appauth"
    if (
        name.startswith("OpenID4VC")
        or name.startswith("OpenID4VP")
        or name.startswith("SIOPv2")
        or name.startswith("connect-key-binding")
        or name.startswith("connect-ephemeral-sub")
        or name.startswith("rp-metadata-choices")
        or name.startswith("eKYC-IDA")
    ):
        return "digital-credentials"
    if name.startswith("federation"):
        return "federation"
    if name.startswith("ipsie"):
        return "ipsie"
    if name == "authzen":
        return "authzen"
    if name == "sharedsignals":
        return "sharedsignals"
    if name == "publication":
        return "publication"
    return "other"


def group_by_repo(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for it in items:
        repo_url = it.get("repository_url", "")
        if not repo_url:
            continue
        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            continue
        full_name = "/".join(parts[-2:])
        counts[full_name] = counts.get(full_name, 0) + 1
    return counts


def main() -> None:
    args = parse_args()
    snapshot_date = args.date or utc_today().isoformat()

    raw_dir = Path(args.raw_root) / snapshot_date
    out_root = Path(args.out_root)

    repos_raw = read_json(raw_dir / "repos.json")
    open_prs_raw = read_json(raw_dir / "open_prs.json")
    open_issues_raw = read_json(raw_dir / "open_issues.json")
    merged_raw = read_json(raw_dir / "merged_prs_30d.json")

    watch_cfg = load_yaml(Path(args.watchlist))
    watch_items = watch_cfg.get("watchlist", [])
    watch_map = {w["repo"]: w for w in watch_items}

    open_prs_by_repo = group_by_repo(open_prs_raw.get("items", []))
    open_issues_by_repo = group_by_repo(open_issues_raw.get("items", []))
    merged_by_repo = group_by_repo(merged_raw.get("items", []))

    repos = []
    for r in repos_raw.get("items", []):
        full_name = r.get("full_name")
        watch = watch_map.get(full_name)
        item = {
            "snapshot_date": snapshot_date,
            "name": r.get("name"),
            "full_name": full_name,
            "html_url": r.get("html_url"),
            "category": classify(r.get("name", "")),
            "default_branch": r.get("default_branch"),
            "archived": bool(r.get("archived", False)),
            "stars": int(r.get("stargazers_count", 0)),
            "forks": int(r.get("forks_count", 0)),
            "open_prs": int(open_prs_by_repo.get(full_name, 0)),
            "open_issues": int(open_issues_by_repo.get(full_name, 0)),
            "merged_prs_30d": int(merged_by_repo.get(full_name, 0)),
            "pushed_at": r.get("pushed_at"),
            "updated_at": r.get("updated_at"),
            "created_at": r.get("created_at"),
            "days_since_push": days_since(r.get("pushed_at")),
            "watchlist": watch is not None,
            "watch_weight": float(watch.get("weight", 1.0)) if watch else 1.0,
            "watch_note": watch.get("note", "") if watch else "",
        }
        repos.append(item)

    repos.sort(key=lambda x: x["full_name"])

    normalized = {
        "generated_at": utc_now_iso(),
        "snapshot_date": snapshot_date,
        "source": {
            "repos_count": len(repos),
            "open_prs_total": open_prs_raw.get("total_count", 0),
            "open_issues_total": open_issues_raw.get("total_count", 0),
            "merged_prs_30d_total": merged_raw.get("total_count", 0),
            "fetch_errors": {
                "open_prs": open_prs_raw.get("error"),
                "open_issues": open_issues_raw.get("error"),
                "merged_prs_30d": merged_raw.get("error"),
            },
        },
        "repos": repos,
    }

    out_file = out_root / f"repos-{snapshot_date}.json"
    latest_file = out_root / "latest.json"
    write_json(out_file, normalized)
    write_json(latest_file, normalized)

    print(f"Normalized snapshot: {snapshot_date}")
    print(f"Output: {out_file}")


if __name__ == "__main__":
    main()
