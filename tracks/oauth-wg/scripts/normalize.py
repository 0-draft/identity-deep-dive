#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def parse_state_id(uri: str) -> int | None:
    m = re.search(r"/doc/state/(\d+)/", uri or "")
    if not m:
        return None
    return int(m.group(1))


def parse_mailarchive_messages(raw_html: str) -> list[dict[str, str]]:
    pattern = re.compile(r'<a[^>]+href="(/arch/msg/oauth/[^"]+/)"[^>]*>(.*?)</a>', re.S)
    seen: set[str] = set()
    messages: list[dict[str, str]] = []

    for href, subject in pattern.findall(raw_html):
        if href in seen:
            continue
        seen.add(href)
        cleaned = re.sub(r"<[^>]+>", "", subject)
        cleaned = html.unescape(cleaned).strip()
        if not cleaned:
            continue
        messages.append(
            {
                "subject": cleaned,
                "url": f"https://mailarchive.ietf.org{href}",
            }
        )
        if len(messages) >= 300:
            break
    return messages


def pick_latest_snapshot(root_dir: pathlib.Path) -> pathlib.Path:
    snapshots_dir = root_dir / "data" / "snapshots"
    candidates = [p for p in snapshots_dir.iterdir() if p.is_dir()]
    if not candidates:
        raise SystemExit("no snapshot directories found in data/snapshots")
    return sorted(candidates)[-1]


def simplify_repo_name(repository_url: str) -> str:
    parts = repository_url.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return repository_url


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot-dir",
        help="Path to snapshot dir. If omitted, latest snapshot is used.",
    )
    args = parser.parse_args()

    root_dir = pathlib.Path(__file__).resolve().parents[1]
    snapshot_dir = pathlib.Path(args.snapshot_dir) if args.snapshot_dir else pick_latest_snapshot(root_dir)
    normalized_dir = root_dir / "data" / "normalized"

    github_dir = snapshot_dir / "github"
    datatracker_dir = snapshot_dir / "datatracker"
    mailarchive_dir = snapshot_dir / "mailarchive"

    repos_raw = load_json(github_dir / "repos.json")
    events_raw = load_json(github_dir / "org_events.json")
    prs_raw = load_json(github_dir / "prs_recent.json")
    issues_raw = load_json(github_dir / "issues_recent.json")

    group_raw = load_json(datatracker_dir / "group.json")
    states_raw = load_json(datatracker_dir / "states.json")
    drafts_raw = load_json(datatracker_dir / "oauth_drafts_active.json")

    mailarchive_html = (mailarchive_dir / "browse_oauth.html").read_text(encoding="utf-8") if (mailarchive_dir / "browse_oauth.html").exists() else ""

    state_map: dict[int, dict[str, str]] = {}
    for obj in states_raw.get("objects", []):
        sid = obj.get("id")
        if isinstance(sid, int):
            state_map[sid] = {
                "name": obj.get("name", ""),
                "slug": obj.get("slug", ""),
                "type": obj.get("type", ""),
            }

    drafts_normalized: list[dict[str, Any]] = []
    for obj in drafts_raw.get("objects", []):
        state_ids: list[int] = []
        state_labels: list[str] = []
        state_types: list[str] = []
        for uri in obj.get("states", []):
            sid = parse_state_id(uri)
            if sid is None:
                continue
            state_ids.append(sid)
            if sid in state_map:
                state_labels.append(state_map[sid]["name"])
                state_types.append(state_map[sid]["type"])

        drafts_normalized.append(
            {
                "name": obj.get("name", ""),
                "rev": obj.get("rev", ""),
                "title": obj.get("title", ""),
                "updated_at": obj.get("time", ""),
                "expires_at": obj.get("expires", ""),
                "pages": obj.get("pages", 0),
                "state_ids": state_ids,
                "state_labels": state_labels,
                "state_types": state_types,
                "datatracker_url": f"https://datatracker.ietf.org/doc/{obj.get('name', '')}/",
            }
        )

    drafts_normalized.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    repos_normalized = []
    for repo in repos_raw:
        repos_normalized.append(
            {
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", ""),
                "pushed_at": repo.get("pushed_at", ""),
                "updated_at": repo.get("updated_at", ""),
                "open_issues_count": repo.get("open_issues_count", 0),
                "html_url": repo.get("html_url", ""),
                "default_branch": repo.get("default_branch", ""),
            }
        )
    repos_normalized.sort(key=lambda x: x.get("pushed_at", ""), reverse=True)

    events_normalized = []
    for event in events_raw:
        payload = event.get("payload", {})
        events_normalized.append(
            {
                "type": event.get("type", ""),
                "created_at": event.get("created_at", ""),
                "repo": event.get("repo", {}).get("name", ""),
                "actor": event.get("actor", {}).get("login", ""),
                "action": payload.get("action", ""),
                "ref": payload.get("ref", ""),
                "issue_number": payload.get("issue", {}).get("number"),
                "issue_title": payload.get("issue", {}).get("title"),
                "pr_number": payload.get("pull_request", {}).get("number"),
                "pr_title": payload.get("pull_request", {}).get("title"),
            }
        )

    def normalize_search_items(raw: dict[str, Any]) -> list[dict[str, Any]]:
        out = []
        for item in raw.get("items", []):
            out.append(
                {
                    "number": item.get("number"),
                    "title": item.get("title", ""),
                    "state": item.get("state", ""),
                    "updated_at": item.get("updated_at", ""),
                    "created_at": item.get("created_at", ""),
                    "comments": item.get("comments", 0),
                    "repo_full_name": simplify_repo_name(item.get("repository_url", "")),
                    "html_url": item.get("html_url", ""),
                    "labels": [lbl.get("name", "") for lbl in item.get("labels", [])],
                }
            )
        return out

    prs_normalized = normalize_search_items(prs_raw)
    issues_normalized = normalize_search_items(issues_raw)

    mailarchive_messages = parse_mailarchive_messages(mailarchive_html)
    weekly_digest = [m for m in mailarchive_messages if "Weekly github digest" in m["subject"]]

    metadata = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "snapshot_dir": str(snapshot_dir),
        "oauth_group": group_raw.get("objects", [{}])[0] if group_raw.get("objects") else {},
        "counts": {
            "drafts": len(drafts_normalized),
            "repos": len(repos_normalized),
            "events": len(events_normalized),
            "prs": len(prs_normalized),
            "issues": len(issues_normalized),
            "mailarchive_messages": len(mailarchive_messages),
            "mailarchive_weekly_digest": len(weekly_digest),
        },
    }

    save_json(normalized_dir / "drafts.json", drafts_normalized)
    save_json(normalized_dir / "repos.json", repos_normalized)
    save_json(normalized_dir / "events.json", events_normalized)
    save_json(normalized_dir / "prs.json", prs_normalized)
    save_json(normalized_dir / "issues.json", issues_normalized)
    save_json(
        normalized_dir / "mailarchive.json",
        {
            "messages": mailarchive_messages,
            "weekly_digest_count": len(weekly_digest),
            "weekly_digest_latest": weekly_digest[0] if weekly_digest else None,
        },
    )
    save_json(normalized_dir / "metadata.json", metadata)

    print(f"normalized snapshot: {snapshot_dir}")


if __name__ == "__main__":
    main()
