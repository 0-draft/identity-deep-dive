#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from typing import Any

from _common import (
    ROOT,
    iso_now,
    load_yaml,
    parse_iso8601,
    read_json,
    today_utc,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score oauth-wg drafts and write candidates.json")
    p.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def lifecycle_score(state_labels: list[str], rules: list[dict[str, Any]]) -> tuple[int, str]:
    best = (0, "no lifecycle signal")
    for label in state_labels:
        for rule in rules:
            if rule["match"] in label and int(rule["points"]) > best[0]:
                best = (int(rule["points"]), label)
    return best


def recency_points(updated: dt.datetime | None, now: dt.datetime, rules: list[dict[str, Any]]) -> tuple[int, str]:
    if updated is None:
        return 0, ""
    age_days = (now - updated).days
    for rule in rules:
        if age_days <= int(rule["within_days"]):
            return int(rule["points"]), f"updated within {rule['within_days']} days"
    return 0, ""


def open_issue_points(open_issues: int, rules: list[dict[str, Any]]) -> int:
    for rule in rules:
        if open_issues >= int(rule["at_least"]):
            return int(rule["points"])
    return 0


def inferred_draft_from_repo(repo_name: str) -> str | None:
    if repo_name.startswith("draft-ietf-oauth-"):
        return repo_name
    if repo_name.startswith("oauth-"):
        return f"draft-ietf-{repo_name}"
    return None


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    state = read_json(ROOT / "data" / "normalized" / "state.json")
    cfg = load_yaml(ROOT / "config" / "scoring.yaml")
    aliases = read_json(ROOT / "config" / "draft_aliases.json").get("repo_to_draft", {})

    activity_cfg = cfg.get("activity", {})
    now = dt.datetime.now(dt.timezone.utc)
    horizon = now - dt.timedelta(days=int(cfg.get("activity_window_days", 14)))

    drafts = state.get("drafts", [])
    repos = state.get("repos", [])
    events = state.get("org_events", [])
    prs = state.get("prs", [])
    issues = state.get("issues", [])

    repo_to_draft = dict(aliases)
    for repo in repos:
        name = repo.get("name", "")
        if name in repo_to_draft:
            continue
        inferred = inferred_draft_from_repo(name)
        if inferred:
            repo_to_draft[name] = inferred

    draft_to_repos: dict[str, list[str]] = {}
    for repo_name, draft_name in repo_to_draft.items():
        draft_to_repos.setdefault(draft_name, []).append(repo_name)

    repo_open_issues = {r.get("name", ""): int(r.get("open_issues_count", 0)) for r in repos}

    activity_weight: dict[str, int] = {}
    event_w = int(activity_cfg.get("event_weight", 1))
    pr_w = int(activity_cfg.get("pr_weight", 3))
    issue_w = int(activity_cfg.get("issue_weight", 2))

    for e in events:
        created = parse_iso8601(e.get("created_at", ""))
        if created is None or created < horizon:
            continue
        repo_full = e.get("repo", "")
        repo_name = repo_full.split("/")[-1] if repo_full else ""
        activity_weight[repo_name] = activity_weight.get(repo_name, 0) + event_w

    for pr in prs:
        updated = parse_iso8601(pr.get("updated_at", ""))
        if updated is None or updated < horizon:
            continue
        repo_name = (pr.get("repo_full_name", "") or "").split("/")[-1]
        activity_weight[repo_name] = activity_weight.get(repo_name, 0) + pr_w

    for issue in issues:
        updated = parse_iso8601(issue.get("updated_at", ""))
        if updated is None or updated < horizon:
            continue
        repo_name = (issue.get("repo_full_name", "") or "").split("/")[-1]
        activity_weight[repo_name] = activity_weight.get(repo_name, 0) + issue_w

    activity_cap = int(activity_cfg.get("cap_points", 30))
    activity_mult = int(activity_cfg.get("multiplier", 2))

    candidates: list[dict[str, Any]] = []
    for draft in drafts:
        draft_name = draft.get("name", "")
        reasons: list[str] = []
        score = 0

        state_score, state_reason = lifecycle_score(
            draft.get("state_labels", []), cfg.get("lifecycle_points", [])
        )
        score += state_score
        if state_score > 0:
            reasons.append(f"lifecycle: {state_reason} (+{state_score})")

        rec_score, rec_reason = recency_points(
            parse_iso8601(draft.get("updated_at", "")),
            now,
            cfg.get("recency_points", []),
        )
        score += rec_score
        if rec_score > 0:
            reasons.append(f"{rec_reason} (+{rec_score})")

        linked = draft_to_repos.get(draft_name, [])
        repo_name = linked[0] if linked else ""
        activity = sum(activity_weight.get(r, 0) for r in linked)
        if activity > 0:
            add = min(activity_cap, activity * activity_mult)
            score += add
            reasons.append(f"repo activity: {activity} (+{add})")

        open_issues = sum(repo_open_issues.get(r, 0) for r in linked)
        oi_score = open_issue_points(open_issues, cfg.get("open_issue_points", []))
        if oi_score > 0:
            score += oi_score
            reasons.append(f"open issues: {open_issues} (+{oi_score})")

        candidates.append(
            {
                "draft_name": draft_name,
                "title": draft.get("title", ""),
                "score": score,
                "updated_at": draft.get("updated_at", ""),
                "state_labels": draft.get("state_labels", []),
                "repo": repo_name,
                "activity": activity,
                "open_issues": open_issues,
                "reasons": reasons,
            }
        )

    candidates.sort(key=lambda x: (x["score"], x["updated_at"]), reverse=True)

    out = {
        "generated_at": iso_now(),
        "snapshot_date": snapshot_date.isoformat(),
        "candidates": candidates,
    }
    write_json(ROOT / "data" / "normalized" / "candidates.json", out)
    snapshot_path = (
        ROOT / "data" / "snapshots" / snapshot_date.isoformat() / "candidates.json"
    )
    write_json(snapshot_path, out)

    print(f"score: candidates={len(candidates)}")


if __name__ == "__main__":
    main()
