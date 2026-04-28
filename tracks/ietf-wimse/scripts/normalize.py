from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from _common import ROOT, iso_now, write_json


def read_json(path: Path) -> dict[str, Any]:
    import json

    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    datatracker = read_json(ROOT / "data" / "normalized" / "datatracker.json")
    mailarchive = read_json(ROOT / "data" / "normalized" / "mailarchive.json")
    github = read_json(ROOT / "data" / "normalized" / "github.json")

    active_drafts = datatracker.get("active_drafts", [])
    related_drafts = datatracker.get("related_drafts", [])

    state = {
        "generated_at": iso_now(),
        "sources": {
            "datatracker": datatracker.get("collected_at", ""),
            "mailarchive": mailarchive.get("collected_at", ""),
            "github": github.get("collected_at", ""),
        },
        "active_drafts": active_drafts,
        "related_drafts": related_drafts,
        "meetings": datatracker.get("meetings", []),
        "ad_history": datatracker.get("ad_history", []),
        "mail_posts": mailarchive.get("posts", []),
        "mail_topics": mailarchive.get("topic_counts", []),
        "mail_top_senders": mailarchive.get("top_senders", []),
        "github_repos": github.get("repos", []),
        "stats": {
            "active_drafts": len(active_drafts),
            "related_drafts": len(related_drafts),
            "mail_posts": len(mailarchive.get("posts", [])),
            "github_repos": len(github.get("repos", [])),
            "github_commits": sum(len(r.get("recent_commits", [])) for r in github.get("repos", [])),
        },
    }

    write_json(ROOT / "data" / "normalized" / "state.json", state)

    today = dt.datetime.now(dt.UTC).date()
    snapshot_path = ROOT / "data" / "snapshots" / f"{today:%Y-%m-%d}" / "state.json"
    write_json(snapshot_path, state)

    print(
        "normalize: "
        f"active={state['stats']['active_drafts']} "
        f"related={state['stats']['related_drafts']} "
        f"mail_posts={state['stats']['mail_posts']}"
    )


if __name__ == "__main__":
    main()
