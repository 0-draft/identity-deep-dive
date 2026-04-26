#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import pathlib
from typing import Any

import yaml


def load_json(path: pathlib.Path) -> Any:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def parse_dt(value: str) -> dt.datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


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
    root_dir = pathlib.Path(__file__).resolve().parents[1]
    normalized_dir = root_dir / "data" / "normalized"
    cfg = load_yaml(root_dir / "config" / "scoring.yaml")

    drafts = load_json(normalized_dir / "drafts.json")
    repos = load_json(normalized_dir / "repos.json")
    events = load_json(normalized_dir / "events.json")
    prs = load_json(normalized_dir / "prs.json")
    issues = load_json(normalized_dir / "issues.json")
    metadata = load_json(normalized_dir / "metadata.json")

    aliases = load_json(root_dir / "config" / "draft_aliases.json").get("repo_to_draft", {})
    activity_cfg = cfg.get("activity", {})
    now = dt.datetime.now(dt.timezone.utc)
    horizon = now - dt.timedelta(days=int(cfg.get("activity_window_days", 14)))

    repo_to_draft = dict(aliases)
    for repo in repos:
        repo_name = repo.get("name", "")
        if repo_name in repo_to_draft:
            continue
        inferred = inferred_draft_from_repo(repo_name)
        if inferred:
            repo_to_draft[repo_name] = inferred

    draft_to_repos: dict[str, list[str]] = {}
    for repo_name, draft_name in repo_to_draft.items():
        draft_to_repos.setdefault(draft_name, []).append(repo_name)

    repo_open_issues = {r.get("name", ""): int(r.get("open_issues_count", 0)) for r in repos}

    activity_weight: dict[str, int] = {}
    event_w = int(activity_cfg.get("event_weight", 1))
    pr_w = int(activity_cfg.get("pr_weight", 3))
    issue_w = int(activity_cfg.get("issue_weight", 2))

    for e in events:
        created = parse_dt(e.get("created_at", ""))
        if created is None or created < horizon:
            continue
        repo_full = e.get("repo", "")
        repo_name = repo_full.split("/")[-1] if repo_full else ""
        activity_weight[repo_name] = activity_weight.get(repo_name, 0) + event_w

    for pr in prs:
        updated = parse_dt(pr.get("updated_at", ""))
        if updated is None or updated < horizon:
            continue
        repo_name = pr.get("repo_full_name", "").split("/")[-1]
        activity_weight[repo_name] = activity_weight.get(repo_name, 0) + pr_w

    for issue in issues:
        updated = parse_dt(issue.get("updated_at", ""))
        if updated is None or updated < horizon:
            continue
        repo_name = issue.get("repo_full_name", "").split("/")[-1]
        activity_weight[repo_name] = activity_weight.get(repo_name, 0) + issue_w

    activity_cap = int(activity_cfg.get("cap_points", 30))
    activity_mult = int(activity_cfg.get("multiplier", 2))

    candidates = []
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
            parse_dt(draft.get("updated_at", "")), now, cfg.get("recency_points", [])
        )
        score += rec_score
        if rec_score > 0:
            reasons.append(f"{rec_reason} (+{rec_score})")

        linked_repos = draft_to_repos.get(draft_name, [])
        repo_name = linked_repos[0] if linked_repos else ""
        activity = sum(activity_weight.get(r, 0) for r in linked_repos)
        if activity > 0:
            add = min(activity_cap, activity * activity_mult)
            score += add
            reasons.append(f"repo activity: {activity} (+{add})")

        open_issues = sum(repo_open_issues.get(r, 0) for r in linked_repos)
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

    backlog = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "snapshot_dir": metadata.get("snapshot_dir", ""),
        "candidates": candidates,
    }
    save_json(normalized_dir / "backlog.json", backlog)
    print("scored backlog written to data/normalized/backlog.json")


if __name__ == "__main__":
    main()
