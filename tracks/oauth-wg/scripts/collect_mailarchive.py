#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import re

from _common import (
    ROOT,
    fetch_text,
    iso_now,
    load_sources,
    raw_output_path,
    today_utc,
    write_json,
)


MSG_RE = re.compile(r'<a[^>]+href="(/arch/msg/oauth/[^"]+/)"[^>]*>(.*?)</a>', re.S)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect oauth list mail archive index")
    p.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    sources = load_sources(ROOT / "config" / "sources.yaml")
    cfg = sources["mailarchive"]
    max_messages = int(cfg.get("max_messages", 300))

    raw_html = fetch_text(cfg["browse_url"])
    write_json(
        raw_output_path("mailarchive", snapshot_date),
        {
            "collected_at": iso_now(),
            "snapshot_date": snapshot_date.isoformat(),
            "browse_url": cfg["browse_url"],
            "html_len": len(raw_html),
        },
    )

    seen: set[str] = set()
    messages: list[dict[str, str]] = []
    for href, subject in MSG_RE.findall(raw_html):
        if href in seen:
            continue
        seen.add(href)
        cleaned = re.sub(r"<[^>]+>", "", subject)
        cleaned = html.unescape(cleaned).strip()
        if not cleaned:
            continue
        messages.append(
            {"subject": cleaned, "url": f"https://mailarchive.ietf.org{href}"}
        )
        if len(messages) >= max_messages:
            break

    weekly_digest = [m for m in messages if "Weekly github digest" in m["subject"]]

    normalized = {
        "collected_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "source": "mailarchive",
        "browse_url": cfg["browse_url"],
        "messages": messages,
        "weekly_digest_count": len(weekly_digest),
        "weekly_digest_latest": weekly_digest[0] if weekly_digest else None,
    }
    write_json(ROOT / "data" / "normalized" / "mailarchive.json", normalized)

    print(
        f"collect-mailarchive: messages={len(messages)} "
        f"weekly_digest={len(weekly_digest)}"
    )


if __name__ == "__main__":
    main()
