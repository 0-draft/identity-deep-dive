#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from typing import Any

from _common import (
    ROOT,
    iso_now,
    parse_iso8601,
    read_json,
    today_utc,
    write_text,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Render oauth-wg markdown reports")
    p.add_argument("--mode", choices=["daily", "weekly"], required=True)
    p.add_argument("--date", help="Snapshot date YYYY-MM-DD (default: UTC today)")
    return p.parse_args()


def render_daily(state: dict[str, Any], candidates: dict[str, Any], snapshot_date: dt.date) -> tuple[str, list[str]]:
    drafts = state.get("drafts", [])
    repos = state.get("repos", [])
    events = state.get("org_events", [])
    prs = state.get("prs", [])
    issues = state.get("issues", [])
    mail_msgs = state.get("mail_messages", [])

    top_candidates = candidates.get("candidates", [])[:10]
    top_drafts = drafts[:15]
    top_repos = repos[:12]
    top_prs = prs[:10]
    top_issues = issues[:10]
    top_events = events[:20]
    top_mail = mail_msgs[:8]

    day = snapshot_date.isoformat()

    lines: list[str] = []
    lines.append(f"# OAuth WG Daily Report - {day}")
    lines.append("")
    lines.append(f"- generated_at_utc: `{iso_now()}`")
    lines.append(f"- snapshot_date: `{day}`")
    lines.append("")

    lines.append("## Top Priorities")
    lines.append("")
    lines.append("| Rank | Draft | Score | Updated | Key State | Repo |")
    lines.append("|---|---|---:|---|---|---|")
    for i, c in enumerate(top_candidates, start=1):
        st = ", ".join(c.get("state_labels", [])[:2])
        lines.append(
            f"| {i} | `{c.get('draft_name', '')}` | {c.get('score', 0)} | "
            f"{c.get('updated_at', '')} | {st} | `{c.get('repo', '')}` |"
        )
    lines.append("")

    lines.append("## Active Drafts")
    lines.append("")
    lines.append("| Draft | Rev | Updated | States |")
    lines.append("|---|---:|---|---|")
    for d in top_drafts:
        states = ", ".join(d.get("state_labels", [])[:3])
        lines.append(
            f"| `{d.get('name', '')}` | {d.get('rev', '')} | {d.get('updated_at', '')} | {states} |"
        )
    lines.append("")

    lines.append("## Repo Watch")
    lines.append("")
    lines.append("| Repo | Pushed | Open Issues |")
    lines.append("|---|---|---:|")
    for r in top_repos:
        lines.append(
            f"| `{r.get('full_name', '')}` | {r.get('pushed_at', '')} | "
            f"{r.get('open_issues_count', 0)} |"
        )
    lines.append("")

    lines.append("## Recent Pull Requests")
    lines.append("")
    for pr in top_prs:
        lines.append(
            f"- `{pr.get('repo_full_name', '')}#{pr.get('number', '')}` "
            f"{pr.get('title', '')} ({pr.get('updated_at', '')})"
        )
    lines.append("")

    lines.append("## Recent Issues")
    lines.append("")
    for issue in top_issues:
        lines.append(
            f"- `{issue.get('repo_full_name', '')}#{issue.get('number', '')}` "
            f"{issue.get('title', '')} ({issue.get('updated_at', '')})"
        )
    lines.append("")

    lines.append("## Organization Events")
    lines.append("")
    for e in top_events:
        label = e.get("pr_title") or e.get("issue_title") or e.get("action") or ""
        lines.append(
            f"- `{e.get('created_at', '')}` {e.get('type', '')} "
            f"`{e.get('repo', '')}` {label}"
        )
    lines.append("")

    lines.append("## Mailarchive Signals")
    lines.append("")
    lines.append(
        f"- weekly_digest_count: `{state.get('mail_weekly_digest_count', 0)}`"
    )
    for m in top_mail:
        lines.append(f"- {m.get('subject', '')} - {m.get('url', '')}")
    lines.append("")

    lines.append("## Next Actions")
    lines.append("")
    lines.append("1. Evaluate the top 3 items in `Top Priorities` as weekly deep-dive candidates.")
    lines.append("2. Separately track comment deadlines for `In Last Call` / `In WG Last Call` drafts.")
    lines.append("3. For repos with a sudden spike in activity, create a scaffold in `deep-dives/` to capture key discussion points.")
    lines.append("")

    backlog_lines = [f"# OAuth WG Backlog ({day})", "", f"- generated_at_utc: `{iso_now()}`", ""]
    for c in candidates.get("candidates", [])[:20]:
        backlog_lines.append(
            f"- [ ] `{c.get('draft_name', '')}` score={c.get('score', 0)} "
            f"updated={c.get('updated_at', '')}"
        )
    backlog_lines.append("")

    return "\n".join(lines), backlog_lines


def render_weekly(state: dict[str, Any], candidates: dict[str, Any], snapshot_date: dt.date) -> tuple[str, str]:
    drafts = state.get("drafts", [])
    prs = state.get("prs", [])
    issues = state.get("issues", [])

    now = dt.datetime.combine(snapshot_date, dt.time.max).replace(tzinfo=dt.timezone.utc)
    horizon = now - dt.timedelta(days=7)
    iso_year, iso_week, _ = snapshot_date.isocalendar()
    week_id = f"{iso_year}-W{iso_week:02d}"

    def _within(item: dict[str, Any]) -> bool:
        ts = parse_iso8601(item.get("updated_at", ""))
        return ts is not None and ts >= horizon

    drafts_updated = [d for d in drafts if _within(d)]
    prs_updated = [p for p in prs if _within(p)]
    issues_updated = [i for i in issues if _within(i)]

    cands = candidates.get("candidates", [])

    lines: list[str] = []
    lines.append(f"# OAuth WG Weekly Digest - {week_id}")
    lines.append("")
    lines.append(f"Window: `{horizon.date().isoformat()}` to `{snapshot_date.isoformat()}`")
    lines.append(f"Generated at: `{iso_now()}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Drafts updated this week: `{len(drafts_updated)}`")
    lines.append(f"- PRs touched this week: `{len(prs_updated)}`")
    lines.append(f"- Issues touched this week: `{len(issues_updated)}`")
    lines.append("")

    lines.append("## Drafts Updated This Week")
    lines.append("")
    if not drafts_updated:
        lines.append("- No active drafts updated in the last 7 days.")
    else:
        lines.append("| Draft | Rev | Updated | States |")
        lines.append("|---|---:|---|---|")
        for d in sorted(drafts_updated, key=lambda x: x.get("updated_at", ""), reverse=True):
            states = ", ".join(d.get("state_labels", [])[:3])
            lines.append(
                f"| `{d.get('name', '')}` | {d.get('rev', '')} | "
                f"{d.get('updated_at', '')} | {states} |"
            )
    lines.append("")

    lines.append("## Top Deep-Dive Candidates")
    lines.append("")
    if not cands:
        lines.append("- No scored candidates available.")
    else:
        lines.append("| Rank | Draft | Score | Reasons |")
        lines.append("|---:|---|---:|---|")
        for i, c in enumerate(cands[:10], start=1):
            reasons = "; ".join(c.get("reasons", [])[:3])
            lines.append(
                f"| {i} | `{c.get('draft_name', '')}` | {c.get('score', 0)} | {reasons} |"
            )
    lines.append("")

    lines.append("## Active PRs This Week")
    lines.append("")
    if not prs_updated:
        lines.append("- No PR activity in window.")
    else:
        for pr in sorted(prs_updated, key=lambda x: x.get("updated_at", ""), reverse=True)[:15]:
            lines.append(
                f"- `{pr.get('repo_full_name', '')}#{pr.get('number', '')}` "
                f"{pr.get('title', '')} ({pr.get('updated_at', '')})"
            )
    lines.append("")

    return "\n".join(lines) + "\n", week_id


def main() -> None:
    args = parse_args()
    snapshot_date = (
        dt.date.fromisoformat(args.date) if args.date else today_utc()
    )

    state = read_json(ROOT / "data" / "normalized" / "state.json")
    candidates = read_json(ROOT / "data" / "normalized" / "candidates.json")

    if args.mode == "daily":
        body, backlog_lines = render_daily(state, candidates, snapshot_date)
        out_path = ROOT / "reports" / "daily" / f"{snapshot_date.isoformat()}.md"
        write_text(out_path, body)
        write_text(ROOT / "deep-dives" / "_backlog.md", "\n".join(backlog_lines))
        print(f"report-daily: {out_path}")
        return

    body, week_id = render_weekly(state, candidates, snapshot_date)
    out_path = ROOT / "reports" / "weekly" / f"{week_id}.md"
    write_text(out_path, body)
    print(f"report-weekly: {out_path}")


if __name__ == "__main__":
    main()
