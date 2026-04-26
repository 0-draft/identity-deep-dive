#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import pathlib
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    root_dir = pathlib.Path(__file__).resolve().parents[1]
    normalized_dir = root_dir / "data" / "normalized"

    metadata = load_json(normalized_dir / "metadata.json")
    drafts = load_json(normalized_dir / "drafts.json")
    repos = load_json(normalized_dir / "repos.json")
    events = load_json(normalized_dir / "events.json")
    prs = load_json(normalized_dir / "prs.json")
    issues = load_json(normalized_dir / "issues.json")
    mailarchive = load_json(normalized_dir / "mailarchive.json")
    backlog = load_json(normalized_dir / "backlog.json")

    now = dt.datetime.now(dt.timezone.utc)
    day = now.strftime("%Y-%m-%d")
    generated_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    top_candidates = backlog.get("candidates", [])[:10]
    top_drafts = drafts[:15]
    top_repos = repos[:12]
    top_prs = prs[:10]
    top_issues = issues[:10]
    top_events = events[:20]
    top_mail = mailarchive.get("messages", [])[:8]

    lines: list[str] = []
    lines.append(f"# OAuth WG Daily Report - {day}")
    lines.append("")
    lines.append(f"- generated_at_utc: `{generated_at}`")
    lines.append(f"- snapshot: `{metadata.get('snapshot_dir', '')}`")
    lines.append("")
    lines.append("## Top Priorities")
    lines.append("")
    lines.append("| Rank | Draft | Score | Updated | Key State | Repo |")
    lines.append("|---|---|---:|---|---|---|")
    for i, c in enumerate(top_candidates, start=1):
        state = ", ".join(c.get("state_labels", [])[:2])
        lines.append(
            f"| {i} | `{c.get('draft_name', '')}` | {c.get('score', 0)} | {c.get('updated_at', '')} | {state} | `{c.get('repo', '')}` |"
        )
    lines.append("")

    lines.append("## Active Drafts")
    lines.append("")
    lines.append("| Draft | Rev | Updated | States |")
    lines.append("|---|---:|---|---|")
    for d in top_drafts:
        states = ", ".join(d.get("state_labels", [])[:3])
        lines.append(f"| `{d.get('name', '')}` | {d.get('rev', '')} | {d.get('updated_at', '')} | {states} |")
    lines.append("")

    lines.append("## Repo Watch")
    lines.append("")
    lines.append("| Repo | Pushed | Open Issues |")
    lines.append("|---|---|---:|")
    for r in top_repos:
        lines.append(
            f"| `{r.get('full_name', '')}` | {r.get('pushed_at', '')} | {r.get('open_issues_count', 0)} |"
        )
    lines.append("")

    lines.append("## Recent Pull Requests")
    lines.append("")
    for pr in top_prs:
        lines.append(
            f"- `{pr.get('repo_full_name', '')}#{pr.get('number', '')}` {pr.get('title', '')} ({pr.get('updated_at', '')})"
        )
    lines.append("")

    lines.append("## Recent Issues")
    lines.append("")
    for issue in top_issues:
        lines.append(
            f"- `{issue.get('repo_full_name', '')}#{issue.get('number', '')}` {issue.get('title', '')} ({issue.get('updated_at', '')})"
        )
    lines.append("")

    lines.append("## Organization Events")
    lines.append("")
    for e in top_events:
        label = e.get("pr_title") or e.get("issue_title") or e.get("action") or ""
        lines.append(f"- `{e.get('created_at', '')}` {e.get('type', '')} `{e.get('repo', '')}` {label}")
    lines.append("")

    lines.append("## Mailarchive Signals")
    lines.append("")
    lines.append(f"- weekly_digest_count: `{mailarchive.get('weekly_digest_count', 0)}`")
    for m in top_mail:
        lines.append(f"- {m.get('subject', '')} - {m.get('url', '')}")
    lines.append("")

    lines.append("## Next Actions")
    lines.append("")
    lines.append("1. Evaluate the top 3 items in `Top Priorities` as weekly deep-dive candidates.")
    lines.append("2. Separately track comment deadlines for `In Last Call` / `In WG Last Call` drafts.")
    lines.append("3. For repos with a sudden spike in activity, create a scaffold in `deep-dives/` to capture key discussion points.")
    lines.append("")

    report_body = "\n".join(lines)
    report_path = root_dir / "reports" / "daily" / f"{day}.md"
    write_text(report_path, report_body)

    backlog_lines = []
    backlog_lines.append(f"# OAuth WG Backlog ({day})")
    backlog_lines.append("")
    backlog_lines.append(f"- generated_at_utc: `{generated_at}`")
    backlog_lines.append("")
    for c in backlog.get("candidates", [])[:20]:
        backlog_lines.append(
            f"- [ ] `{c.get('draft_name', '')}` score={c.get('score', 0)} updated={c.get('updated_at', '')}"
        )
    backlog_lines.append("")
    write_text(root_dir / "deep-dives" / "_backlog.md", "\n".join(backlog_lines))

    print(f"daily report written: {report_path}")


if __name__ == "__main__":
    main()
