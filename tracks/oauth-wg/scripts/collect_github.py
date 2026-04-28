#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from typing import Any
from urllib.parse import quote_plus

import requests

from _common import (
    ROOT,
    fetch_json,
    github_paginate,
    iso_now,
    load_sources,
    raw_output_path,
    today_utc,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect oauth-wg GitHub activity")
    p.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def _flatten_search(url: str, max_pages: int) -> dict[str, Any]:
    items: list[Any] = []
    total_count = 0
    error: str | None = None
    pages = 0
    try:
        for page in github_paginate(url, per_page=100, max_pages=max_pages):
            if pages == 0:
                total_count = int(page.get("total_count", 0))
            items.extend(page.get("items", []))
            pages += 1
    except requests.HTTPError as exc:
        error = f"HTTP {exc.response.status_code}: {exc.response.reason}"
    return {"total_count": total_count, "items": items, "error": error}


def _simplify_repo(repository_url: str) -> str:
    parts = (repository_url or "").rstrip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return repository_url or ""


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    sources = load_sources(ROOT / "config" / "sources.yaml")
    gh = sources["github"]
    api_base = gh.get("api_base", "https://api.github.com").rstrip("/")
    org = gh["org"]
    repo_pages = int(gh.get("repo_pages", 5))
    search_max_pages = int(gh.get("search_max_pages", 5))
    events_pages = int(gh.get("events_pages", 1))

    repos: list[dict[str, Any]] = []
    for page in github_paginate(
        f"{api_base}/orgs/{org}/repos?type=public", per_page=100, max_pages=repo_pages
    ):
        if not isinstance(page, list):
            break
        repos.extend(page)
        if len(page) < 100:
            break

    org_events: list[dict[str, Any]] = []
    for page in github_paginate(
        f"{api_base}/orgs/{org}/events", per_page=100, max_pages=events_pages
    ):
        if not isinstance(page, list):
            break
        org_events.extend(page)
        if len(page) < 100:
            break

    prs_search = _flatten_search(
        f"{api_base}/search/issues?q={quote_plus(f'org:{org} is:pr')}&sort=updated&order=desc",
        max_pages=search_max_pages,
    )
    issues_search = _flatten_search(
        f"{api_base}/search/issues?q={quote_plus(f'org:{org} is:issue')}&sort=updated&order=desc",
        max_pages=search_max_pages,
    )

    raw = {
        "collected_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "repos": repos,
        "org_events": org_events,
        "prs": prs_search,
        "issues": issues_search,
    }
    write_json(raw_output_path("github", snapshot_date), raw)

    repos_norm = [
        {
            "name": r.get("name", ""),
            "full_name": r.get("full_name", ""),
            "pushed_at": r.get("pushed_at", ""),
            "updated_at": r.get("updated_at", ""),
            "open_issues_count": int(r.get("open_issues_count", 0)),
            "html_url": r.get("html_url", ""),
            "default_branch": r.get("default_branch", ""),
        }
        for r in repos
    ]
    repos_norm.sort(key=lambda x: x["pushed_at"], reverse=True)

    events_norm = []
    for e in org_events:
        payload = e.get("payload", {}) or {}
        events_norm.append(
            {
                "type": e.get("type", ""),
                "created_at": e.get("created_at", ""),
                "repo": (e.get("repo") or {}).get("name", ""),
                "actor": (e.get("actor") or {}).get("login", ""),
                "action": payload.get("action", ""),
                "ref": payload.get("ref", ""),
                "issue_number": (payload.get("issue") or {}).get("number"),
                "issue_title": (payload.get("issue") or {}).get("title"),
                "pr_number": (payload.get("pull_request") or {}).get("number"),
                "pr_title": (payload.get("pull_request") or {}).get("title"),
            }
        )

    def _norm_search(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for item in items:
            out.append(
                {
                    "number": item.get("number"),
                    "title": item.get("title", ""),
                    "state": item.get("state", ""),
                    "updated_at": item.get("updated_at", ""),
                    "created_at": item.get("created_at", ""),
                    "comments": int(item.get("comments", 0)),
                    "repo_full_name": _simplify_repo(item.get("repository_url", "")),
                    "html_url": item.get("html_url", ""),
                    "labels": [(l or {}).get("name", "") for l in item.get("labels", [])],
                }
            )
        return out

    normalized = {
        "collected_at": raw["collected_at"],
        "snapshot_date": raw["snapshot_date"],
        "source": "github",
        "repos": repos_norm,
        "org_events": events_norm,
        "prs": _norm_search(prs_search["items"]),
        "issues": _norm_search(issues_search["items"]),
        "fetch_errors": {
            "prs": prs_search["error"],
            "issues": issues_search["error"],
        },
    }
    write_json(ROOT / "data" / "normalized" / "github.json", normalized)

    print(
        f"collect-github: repos={len(repos_norm)} "
        f"events={len(events_norm)} prs={len(normalized['prs'])} "
        f"issues={len(normalized['issues'])}"
    )


if __name__ == "__main__":
    main()
