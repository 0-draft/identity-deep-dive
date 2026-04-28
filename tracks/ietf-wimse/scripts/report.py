from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

from _common import ROOT, write_text


def read_json(path: Path) -> dict[str, Any]:
    import json

    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def render_daily(state: dict[str, Any], candidates: dict[str, Any]) -> str:
    lines: list[str] = []
    today = dt.date.today().isoformat()
    lines.append(f"# WIMSE Daily Report ({today})")
    lines.append("")
    lines.append(f"Generated at: {state.get('generated_at', '')}")
    lines.append("")

    stats = state.get("stats", {})
    lines.append("## Snapshot")
    lines.append("")
    lines.append(f"- Active WG drafts: {stats.get('active_drafts', 0)}")
    lines.append(f"- Related drafts: {stats.get('related_drafts', 0)}")
    lines.append(f"- Mailing-list posts scanned: {stats.get('mail_posts', 0)}")
    lines.append(f"- Tracked GitHub repos: {stats.get('github_repos', 0)}")
    lines.append("")

    lines.append("## Active WG Drafts")
    lines.append("")
    lines.append("| Draft | Date | Title |")
    lines.append("| --- | --- | --- |")
    for draft in sorted(state.get("active_drafts", []), key=lambda d: d.get("date", ""), reverse=True):
        lines.append(
            f"| {draft.get('name_rev', '')} | {draft.get('date', '')} | {draft.get('title', '')} |"
        )
    lines.append("")

    lines.append("## Recent Related Drafts")
    lines.append("")
    lines.append("| Draft | Date | Title |")
    lines.append("| --- | --- | --- |")
    for draft in sorted(state.get("related_drafts", []), key=lambda d: d.get("date", ""), reverse=True)[:10]:
        lines.append(
            f"| {draft.get('name_rev', '')} | {draft.get('date', '')} | {draft.get('title', '')} |"
        )
    lines.append("")

    lines.append("## Mailing List Topics")
    lines.append("")
    if not state.get("mail_topics"):
        lines.append("- No mailing-list topics extracted.")
    else:
        for topic in state["mail_topics"][:10]:
            lines.append(f"- {topic.get('topic', 'unknown')}: {topic.get('count', 0)}")
    lines.append("")

    lines.append("## Recent GitHub Activity")
    lines.append("")
    lines.append("| Repository | Latest Commit |")
    lines.append("| --- | --- |")
    for repo in sorted(state.get("github_repos", []), key=lambda r: r.get("latest_commit_date", ""), reverse=True):
        lines.append(f"| {repo.get('repo', '')} | {repo.get('latest_commit_date', '')} |")
    lines.append("")

    lines.append("## Top Deep-Dive Candidates")
    lines.append("")
    ranked = candidates.get("candidates", [])
    if not ranked:
        lines.append("- No candidates above threshold.")
    else:
        for item in ranked[:10]:
            lines.append(f"- [{item.get('score', 0)}] {item.get('title', '')}")
    lines.append("")

    return "\n".join(lines)


def recent_snapshot_paths(limit: int = 8) -> list[Path]:
    root = ROOT / "data" / "snapshots"
    if not root.exists():
        return []
    paths = [p / "state.json" for p in root.iterdir() if p.is_dir() and (p / "state.json").exists()]
    return sorted(paths)[-limit:]


def render_weekly(current: dict[str, Any]) -> str:
    lines: list[str] = []
    today = dt.date.today().isoformat()
    lines.append(f"# WIMSE Weekly Digest ({today})")
    lines.append("")
    lines.append(f"Generated at: {current.get('generated_at', '')}")
    lines.append("")

    snapshots = recent_snapshot_paths(limit=8)
    lines.append("## Snapshot Coverage")
    lines.append("")
    lines.append(f"- Snapshots available: {len(snapshots)}")
    if snapshots:
        lines.append(f"- First snapshot in window: {snapshots[0].parent.name}")
        lines.append(f"- Last snapshot in window: {snapshots[-1].parent.name}")
    lines.append("")

    lines.append("## Draft Movement")
    lines.append("")
    if len(snapshots) < 2:
        lines.append("- Not enough snapshots to compute weekly diff.")
    else:
        prev = read_json(snapshots[-2])
        curr = current

        prev_set = {d.get("name_rev", "") for d in prev.get("active_drafts", [])}
        curr_set = {d.get("name_rev", "") for d in curr.get("active_drafts", [])}

        added = sorted(curr_set - prev_set)
        removed = sorted(prev_set - curr_set)

        if not added and not removed:
            lines.append("- No active-draft list change since previous snapshot.")
        else:
            if added:
                lines.append("- Added/updated active draft revisions:")
                for item in added:
                    lines.append(f"  - {item}")
            if removed:
                lines.append("- Removed/replaced active draft revisions:")
                for item in removed:
                    lines.append(f"  - {item}")
    lines.append("")

    lines.append("## Current Hot Topics")
    lines.append("")
    topics = current.get("mail_topics", [])
    if not topics:
        lines.append("- No topic signal from mailing list.")
    else:
        for topic in topics[:10]:
            lines.append(f"- {topic.get('topic', 'unknown')}: {topic.get('count', 0)}")
    lines.append("")

    lines.append("## Next Deep-Dive Suggestions")
    lines.append("")
    candidates = read_json(ROOT / "data" / "normalized" / "candidates.json").get("candidates", [])
    if not candidates:
        lines.append("- No candidates above threshold.")
    else:
        for item in candidates[:10]:
            lines.append(f"- [{item.get('score', 0)}] {item.get('title', '')}")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render WIMSE markdown reports")
    parser.add_argument("--mode", choices=["daily", "weekly"], default="daily")
    args = parser.parse_args()

    state = read_json(ROOT / "data" / "normalized" / "state.json")
    candidates = read_json(ROOT / "data" / "normalized" / "candidates.json")

    if args.mode == "daily":
        output = render_daily(state, candidates)
        out_path = ROOT / "reports" / "daily" / f"{dt.date.today().isoformat()}.md"
        write_text(out_path, output + "\n")
        print(f"report-daily: {out_path}")
        return

    output = render_weekly(state)
    iso_year, iso_week, _ = dt.date.today().isocalendar()
    out_path = ROOT / "reports" / "weekly" / f"{iso_year}-W{iso_week:02d}.md"
    write_text(out_path, output + "\n")
    print(f"report-weekly: {out_path}")


if __name__ == "__main__":
    main()
