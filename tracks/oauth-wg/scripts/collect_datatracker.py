#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
from typing import Any

from _common import (
    ROOT,
    fetch_json,
    fetch_text,
    iso_now,
    load_sources,
    raw_output_path,
    today_utc,
    write_json,
)


STATE_URI_RE = re.compile(r"/doc/state/(\d+)/")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect IETF Datatracker oauth WG data")
    p.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def _state_id(uri: str) -> int | None:
    m = STATE_URI_RE.search(uri or "")
    return int(m.group(1)) if m else None


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    sources = load_sources(ROOT / "config" / "sources.yaml")
    dt_cfg = sources["datatracker"]

    group = fetch_json(dt_cfg["group_url"])
    states = fetch_json(dt_cfg["states_url"])
    drafts = fetch_json(dt_cfg["active_drafts_url"])
    documents_html = fetch_text(dt_cfg["documents_html_url"])
    meetings_html = fetch_text(dt_cfg["meetings_html_url"])

    raw = {
        "collected_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "group": group,
        "states": states,
        "active_drafts": drafts,
        "documents_html_len": len(documents_html),
        "meetings_html_len": len(meetings_html),
    }
    write_json(raw_output_path("datatracker", snapshot_date), raw)

    state_map: dict[int, dict[str, str]] = {}
    for obj in states.get("objects", []):
        sid = obj.get("id")
        if isinstance(sid, int):
            state_map[sid] = {
                "name": obj.get("name", ""),
                "slug": obj.get("slug", ""),
                "type": obj.get("type", ""),
            }

    drafts_norm: list[dict[str, Any]] = []
    for obj in drafts.get("objects", []):
        sids: list[int] = []
        labels: list[str] = []
        types: list[str] = []
        for uri in obj.get("states", []):
            sid = _state_id(uri)
            if sid is None:
                continue
            sids.append(sid)
            if sid in state_map:
                labels.append(state_map[sid]["name"])
                types.append(state_map[sid]["type"])
        drafts_norm.append(
            {
                "name": obj.get("name", ""),
                "rev": obj.get("rev", ""),
                "title": obj.get("title", ""),
                "updated_at": obj.get("time", ""),
                "expires_at": obj.get("expires", ""),
                "pages": obj.get("pages", 0),
                "state_ids": sids,
                "state_labels": labels,
                "state_types": types,
                "datatracker_url": f"https://datatracker.ietf.org/doc/{obj.get('name', '')}/",
            }
        )
    drafts_norm.sort(key=lambda x: x["updated_at"], reverse=True)

    group_objs = group.get("objects", [])
    normalized = {
        "collected_at": raw["collected_at"],
        "snapshot_date": raw["snapshot_date"],
        "source": "datatracker",
        "oauth_group": group_objs[0] if group_objs else {},
        "drafts": drafts_norm,
    }
    write_json(ROOT / "data" / "normalized" / "datatracker.json", normalized)

    print(f"collect-datatracker: drafts={len(drafts_norm)} states={len(state_map)}")


if __name__ == "__main__":
    main()
