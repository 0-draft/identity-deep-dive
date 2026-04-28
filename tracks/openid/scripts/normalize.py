#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

from _common import (
    ROOT,
    iso_now,
    load_sources,
    read_json,
    today_utc,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalize OpenID per-source data into state.json")
    p.add_argument("--date", help="Snapshot date in YYYY-MM-DD (default: UTC today)")
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


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    github = read_json(ROOT / "data" / "normalized" / "github.json")
    sources = load_sources(ROOT / "config" / "sources.yaml")
    watch_map = {entry["repo"]: entry for entry in sources["github"]["repos"]}

    enriched_repos: list[dict[str, Any]] = []
    for r in github.get("repos", []):
        full = r.get("full_name") or ""
        watch = watch_map.get(full)
        category = (watch and watch.get("category")) or classify(r.get("name", ""))
        enriched_repos.append(
            {
                **r,
                "category": category,
                "watchlist": watch is not None,
                "watch_weight": float(watch["weight"]) if watch else 1.0,
                "watch_note": (watch and watch.get("note")) or "",
            }
        )

    state = {
        "generated_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "sources": {"github": github.get("collected_at", "")},
        "github_org": github.get("org", {}),
        "github_repos": enriched_repos,
        "github_search_totals": github.get("search_totals", {}),
        "fetch_errors": github.get("fetch_errors", {}),
        "stats": {
            "repos": len(enriched_repos),
            "active_30d": sum(
                1 for r in enriched_repos if (r.get("days_since_push") or 99999) <= 30
            ),
            "active_90d": sum(
                1 for r in enriched_repos if (r.get("days_since_push") or 99999) <= 90
            ),
            "archived": sum(1 for r in enriched_repos if r.get("archived")),
            "watchlist_repos": sum(1 for r in enriched_repos if r["watchlist"]),
        },
    }

    write_json(ROOT / "data" / "normalized" / "state.json", state)
    snapshot_path = ROOT / "data" / "snapshots" / snapshot_date.isoformat() / "state.json"
    write_json(snapshot_path, state)

    print(
        f"normalize: repos={state['stats']['repos']} "
        f"active_30d={state['stats']['active_30d']} "
        f"watchlist={state['stats']['watchlist_repos']}"
    )


if __name__ == "__main__":
    main()
