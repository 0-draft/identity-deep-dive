#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path
from urllib.error import HTTPError

from _common import env_token, github_get, github_paginate, read_json, utc_now_iso, utc_today, write_json


ORG = "openid"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch OpenID organization activity data")
    p.add_argument("--date", help="Snapshot date in YYYY-MM-DD (default: UTC today)")
    p.add_argument("--out-root", default="data/raw", help="Raw data root directory")
    p.add_argument("--max-search-pages", type=int, default=10, help="Max pages per search endpoint")
    return p.parse_args()


def fetch_search(query: str, token: str | None, max_pages: int) -> dict:
    items = []
    total = 0
    error: str | None = None

    for page in range(1, max_pages + 1):
        try:
            payload = github_get(
                "/search/issues",
                token=token,
                params={"q": query, "per_page": 100, "page": page},
            )
        except HTTPError as e:
            error = f"HTTP {e.code}: {e.reason}"
            break

        if page == 1:
            total = int(payload.get("total_count", 0))

        page_items = payload.get("items", [])
        if not page_items:
            break

        items.extend(page_items)
        if len(page_items) < 100:
            break

    return {
        "query": query,
        "total_count": total,
        "items": items,
        "error": error,
    }


def reuse_from_previous(path: Path, payload: dict) -> dict:
    if not payload.get("error"):
        return payload
    if not path.exists():
        return payload

    prev = read_json(path)
    prev_total = prev.get("total_count")
    prev_items = prev.get("items")

    if prev_total is not None:
        payload["total_count"] = prev_total
    if isinstance(prev_items, list) and prev_items:
        payload["items"] = prev_items
    payload["reused_previous"] = True
    return payload


def main() -> None:
    args = parse_args()
    snapshot_date = args.date or utc_today().isoformat()
    out_dir = Path(args.out_root) / snapshot_date
    token = env_token()

    org = github_get(f"/orgs/{ORG}", token=token)
    repos = github_paginate(
        f"/orgs/{ORG}/repos",
        token=token,
        params={"type": "public", "sort": "updated", "per_page": 100},
        max_pages=5,
    )

    open_prs = fetch_search(f"org:{ORG} is:pr is:open", token=token, max_pages=args.max_search_pages)
    open_issues = fetch_search(f"org:{ORG} is:issue is:open", token=token, max_pages=args.max_search_pages)

    since = (utc_today() - timedelta(days=30)).isoformat()
    merged_prs_30d = fetch_search(
        f"org:{ORG} is:pr is:merged merged:>={since}",
        token=token,
        max_pages=args.max_search_pages,
    )

    metadata = {
        "fetched_at": utc_now_iso(),
        "snapshot_date": snapshot_date,
        "org": ORG,
    }

    open_prs_path = out_dir / "open_prs.json"
    open_issues_path = out_dir / "open_issues.json"
    merged_path = out_dir / "merged_prs_30d.json"

    open_prs = reuse_from_previous(open_prs_path, open_prs)
    open_issues = reuse_from_previous(open_issues_path, open_issues)
    merged_prs_30d = reuse_from_previous(merged_path, merged_prs_30d)

    write_json(out_dir / "org.json", {**metadata, "data": org})
    write_json(out_dir / "repos.json", {**metadata, "count": len(repos), "items": repos})
    write_json(open_prs_path, {**metadata, **open_prs})
    write_json(open_issues_path, {**metadata, **open_issues})
    write_json(merged_path, {**metadata, **merged_prs_30d, "since": since})

    print(f"Fetched snapshot: {snapshot_date}")
    print(f"Repos: {len(repos)}")
    print(f"Open PRs(total): {open_prs['total_count']}")
    if open_prs.get("error"):
        print(f"Open PRs fetch warning: {open_prs['error']}")
    print(f"Open Issues(total): {open_issues['total_count']}")
    if open_issues.get("error"):
        print(f"Open Issues fetch warning: {open_issues['error']}")
    print(f"Merged PRs 30d(total): {merged_prs_30d['total_count']}")
    if merged_prs_30d.get("error"):
        print(f"Merged PRs fetch warning: {merged_prs_30d['error']}")


if __name__ == "__main__":
    main()
