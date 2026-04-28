#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt

from _common import ROOT, iso_now, read_json, today_utc, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Merge oauth-wg per-source files into state.json")
    p.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    github = read_json(ROOT / "data" / "normalized" / "github.json")
    datatracker = read_json(ROOT / "data" / "normalized" / "datatracker.json")
    mailarchive = read_json(ROOT / "data" / "normalized" / "mailarchive.json")

    state = {
        "generated_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "sources": {
            "github": github.get("collected_at", ""),
            "datatracker": datatracker.get("collected_at", ""),
            "mailarchive": mailarchive.get("collected_at", ""),
        },
        "oauth_group": datatracker.get("oauth_group", {}),
        "drafts": datatracker.get("drafts", []),
        "repos": github.get("repos", []),
        "org_events": github.get("org_events", []),
        "prs": github.get("prs", []),
        "issues": github.get("issues", []),
        "mail_messages": mailarchive.get("messages", []),
        "mail_weekly_digest_count": mailarchive.get("weekly_digest_count", 0),
        "mail_weekly_digest_latest": mailarchive.get("weekly_digest_latest"),
        "fetch_errors": github.get("fetch_errors", {}),
        "stats": {
            "drafts": len(datatracker.get("drafts", [])),
            "repos": len(github.get("repos", [])),
            "org_events": len(github.get("org_events", [])),
            "prs": len(github.get("prs", [])),
            "issues": len(github.get("issues", [])),
            "mail_messages": len(mailarchive.get("messages", [])),
        },
    }

    write_json(ROOT / "data" / "normalized" / "state.json", state)
    snapshot_path = ROOT / "data" / "snapshots" / snapshot_date.isoformat() / "state.json"
    write_json(snapshot_path, state)

    print(
        f"normalize: drafts={state['stats']['drafts']} "
        f"repos={state['stats']['repos']} "
        f"prs={state['stats']['prs']} "
        f"issues={state['stats']['issues']} "
        f"mail={state['stats']['mail_messages']}"
    )


if __name__ == "__main__":
    main()
