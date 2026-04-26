from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from _common import ROOT, compact_whitespace, load_yaml, parse_date, write_json, write_text


def read_json(path: Path) -> dict[str, Any]:
    import json

    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def days_old(date_str: str, today: dt.date) -> int | None:
    parsed = parse_date(date_str)
    if not parsed:
        return None
    return (today - parsed).days


def bonus_for_keywords(text: str, keywords: list[str], bonus_value: int) -> int:
    hay = text.lower()
    for keyword in keywords:
        if keyword.lower() in hay:
            return bonus_value
    return 0


def add_candidate(
    bucket: dict[str, dict[str, Any]],
    title: str,
    score: int,
    rationale: str,
    evidence: str,
) -> None:
    if title not in bucket:
        bucket[title] = {
            "title": title,
            "score": 0,
            "rationales": [],
            "evidence": [],
        }
    bucket[title]["score"] += score
    bucket[title]["rationales"].append(rationale)
    bucket[title]["evidence"].append(evidence)


def main() -> None:
    state = read_json(ROOT / "data" / "normalized" / "wimse_state.json")
    cfg = load_yaml(ROOT / "config" / "scoring.yaml")

    today = dt.date.today()
    recency = cfg["recency_days"]
    weights = cfg["weights"]
    thresholds = cfg["thresholds"]
    priority_keywords = cfg.get("priority_keywords", [])

    candidates: dict[str, dict[str, Any]] = {}

    for draft in state.get("active_drafts", []):
        age = days_old(draft.get("date", ""), today)
        if age is None or age > recency["active_draft_update"]:
            continue

        title = f"Diff active WG draft: {draft.get('name_rev', draft.get('name', 'unknown'))}"
        score = weights["active_draft_update"]
        score += bonus_for_keywords(draft.get("title", ""), priority_keywords, weights["priority_keyword_bonus"])

        add_candidate(
            candidates,
            title,
            score,
            "Recent active WG draft update",
            f"{draft.get('name_rev', '')} ({draft.get('date', 'unknown date')})",
        )

    for draft in state.get("related_drafts", []):
        age = days_old(draft.get("date", ""), today)
        if age is None or age > recency["related_draft_new"]:
            continue

        title = f"Review related draft: {draft.get('name_rev', draft.get('name', 'unknown'))}"
        score = weights["related_draft_new"]
        score += bonus_for_keywords(draft.get("title", ""), priority_keywords, weights["priority_keyword_bonus"])

        add_candidate(
            candidates,
            title,
            score,
            "New or recently updated related draft",
            f"{draft.get('name_rev', '')} ({draft.get('date', 'unknown date')})",
        )

    for topic in state.get("mail_topics", []):
        count = int(topic.get("count", 0))
        if count < thresholds["min_mail_topic_count"]:
            continue

        label = topic.get("topic", "unknown-topic")
        title = f"Investigate mailing-list trend: {label}"
        score = weights["hot_mail_topic"] + min(count, 5)
        score += bonus_for_keywords(label, priority_keywords, weights["priority_keyword_bonus"])

        add_candidate(
            candidates,
            title,
            score,
            "Hot topic on wimse mailing list",
            f"topic={label} count={count}",
        )

    for repo in state.get("github_repos", []):
        latest = repo.get("latest_commit_date", "")
        age = days_old(latest, today)
        if age is None or age > recency["github_activity"]:
            continue

        title = f"Review recent repository activity: {repo.get('repo', 'unknown-repo')}"
        score = weights["github_activity"]
        recent = repo.get("recent_commits", [])
        if recent:
            score += 1
        score += bonus_for_keywords(repo.get("repo", ""), priority_keywords, weights["priority_keyword_bonus"])

        add_candidate(
            candidates,
            title,
            score,
            "Recent commit activity in tracked repository",
            f"latest_commit={latest}",
        )

    threshold = int(thresholds["min_candidate_score"])
    ranked = [
        {
            "title": item["title"],
            "score": item["score"],
            "rationales": sorted(set(item["rationales"])),
            "evidence": sorted(set(item["evidence"])),
        }
        for item in candidates.values()
        if item["score"] >= threshold
    ]
    ranked.sort(key=lambda x: (-x["score"], x["title"]))

    output = {
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "threshold": threshold,
        "candidates": ranked,
    }
    write_json(ROOT / "data" / "normalized" / "candidates.json", output)

    lines: list[str] = [
        "# Deep-Dive Candidate Queue",
        "",
        f"Generated at: {output['generated_at']}",
        "",
        "| Rank | Score | Candidate | Evidence |",
        "| --- | ---: | --- | --- |",
    ]

    if not ranked:
        lines.append("| - | - | No candidates above threshold | - |")
    else:
        for idx, item in enumerate(ranked, start=1):
            evidence = "; ".join(item["evidence"])[:220]
            lines.append(
                f"| {idx} | {item['score']} | {compact_whitespace(item['title'])} | {compact_whitespace(evidence)} |"
            )

    write_text(ROOT / "deep-dives" / "_backlog.md", "\n".join(lines) + "\n")
    print(f"score: candidates={len(ranked)} threshold={threshold}")


if __name__ == "__main__":
    main()
