#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests

from _common import (
    ROOT,
    days_since,
    ensure_dir,
    fetch_json,
    github_paginate,
    iso_now,
    load_sources,
    raw_output_path,
    today_utc,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect OpenID org GitHub activity")
    p.add_argument("--date", help="Snapshot date in YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def _flatten_search(url: str, max_pages: int) -> dict[str, Any]:
    items: list[Any] = []
    total_count = 0
    incomplete = False
    error: str | None = None
    pages = 0
    try:
        for page in github_paginate(url, per_page=100, max_pages=max_pages):
            if pages == 0:
                total_count = int(page.get("total_count", 0))
            incomplete = incomplete or bool(page.get("incomplete_results", False))
            items.extend(page.get("items", []))
            pages += 1
    except requests.HTTPError as exc:
        error = f"HTTP {exc.response.status_code}: {exc.response.reason}"
    return {
        "total_count": total_count,
        "incomplete_results": incomplete,
        "items": items,
        "error": error,
    }


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    sources = load_sources(ROOT / "config" / "sources.yaml")
    gh = sources.get("github") or {}
    api_base = gh.get("api_base", "https://api.github.com").rstrip("/")
    org = gh["org"]
    repo_pages = int(gh.get("repo_pages", 5))
    search_max_pages = int(gh.get("search_max_pages", 10))
    lookback_days = int(gh.get("merged_lookback_days", 30))

    org_meta = fetch_json(f"{api_base}/orgs/{org}")

    repos: list[dict[str, Any]] = []
    for page in github_paginate(
        f"{api_base}/orgs/{org}/repos?type=public&sort=updated",
        per_page=100,
        max_pages=repo_pages,
    ):
        if not isinstance(page, list):
            break
        repos.extend(page)
        if len(page) < 100:
            break

    since = (snapshot_date - dt.timedelta(days=lookback_days)).isoformat()
    open_prs = _flatten_search(
        f"{api_base}/search/issues?q={quote_plus(f'org:{org} is:pr is:open')}",
        max_pages=search_max_pages,
    )
    open_issues = _flatten_search(
        f"{api_base}/search/issues?q={quote_plus(f'org:{org} is:issue is:open')}",
        max_pages=search_max_pages,
    )
    merged_30d = _flatten_search(
        f"{api_base}/search/issues?q={quote_plus(f'org:{org} is:pr is:merged merged:>={since}')}",
        max_pages=search_max_pages,
    )
    merged_30d["since"] = since

    raw = {
        "collected_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "org": org_meta,
        "repos": repos,
        "open_prs": open_prs,
        "open_issues": open_issues,
        "merged_prs_30d": merged_30d,
    }
    write_json(raw_output_path("github", snapshot_date), raw)

    def _by_repo(items: list[dict[str, Any]]) -> dict[str, int]:
        out: dict[str, int] = {}
        for it in items:
            url = it.get("repository_url", "")
            if not url:
                continue
            parts = url.rstrip("/").split("/")
            if len(parts) < 2:
                continue
            full = "/".join(parts[-2:])
            out[full] = out.get(full, 0) + 1
        return out

    per_repo = {
        "open_prs": _by_repo(open_prs["items"]),
        "open_issues": _by_repo(open_issues["items"]),
        "merged_prs_30d": _by_repo(merged_30d["items"]),
    }

    normalized_repos: list[dict[str, Any]] = []
    for r in repos:
        full = r.get("full_name") or ""
        normalized_repos.append(
            {
                "name": r.get("name"),
                "full_name": full,
                "html_url": r.get("html_url"),
                "default_branch": r.get("default_branch"),
                "archived": bool(r.get("archived", False)),
                "stars": int(r.get("stargazers_count", 0)),
                "forks": int(r.get("forks_count", 0)),
                "pushed_at": r.get("pushed_at"),
                "updated_at": r.get("updated_at"),
                "created_at": r.get("created_at"),
                "days_since_push": days_since(r.get("pushed_at")),
                "open_prs": per_repo["open_prs"].get(full, 0),
                "open_issues": per_repo["open_issues"].get(full, 0),
                "merged_prs_30d": per_repo["merged_prs_30d"].get(full, 0),
            }
        )
    normalized_repos.sort(key=lambda x: x["full_name"] or "")

    normalized = {
        "collected_at": raw["collected_at"],
        "snapshot_date": raw["snapshot_date"],
        "source": "github",
        "org": {
            "login": org_meta.get("login"),
            "name": org_meta.get("name"),
            "html_url": org_meta.get("html_url"),
            "public_repos": org_meta.get("public_repos"),
        },
        "repos": normalized_repos,
        "search_totals": {
            "open_prs": open_prs["total_count"],
            "open_issues": open_issues["total_count"],
            "merged_prs_30d": merged_30d["total_count"],
            "since": since,
        },
        "fetch_errors": {
            "open_prs": open_prs["error"],
            "open_issues": open_issues["error"],
            "merged_prs_30d": merged_30d["error"],
        },
    }
    out_path = ROOT / "data" / "normalized" / "github.json"
    ensure_dir(out_path.parent)
    write_json(out_path, normalized)

    print(
        f"collect-github: repos={len(normalized_repos)} "
        f"open_prs={open_prs['total_count']} "
        f"open_issues={open_issues['total_count']} "
        f"merged_30d={merged_30d['total_count']}"
    )


if __name__ == "__main__":
    main()
