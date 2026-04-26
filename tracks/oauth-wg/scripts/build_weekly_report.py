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


def parse_dt(value: str) -> dt.datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def main() -> None:
    root_dir = pathlib.Path(__file__).resolve().parents[1]
    normalized_dir = root_dir / "data" / "normalized"

    drafts = load_json(normalized_dir / "drafts.json")
    prs = load_json(normalized_dir / "prs.json")
    issues = load_json(normalized_dir / "issues.json")
    backlog = load_json(normalized_dir / "backlog.json")

    now = dt.datetime.now(dt.timezone.utc)
    horizon = now - dt.timedelta(days=7)
    iso_year, iso_week, _ = now.date().isocalendar()
    week_id = f"{iso_year}-W{iso_week:02d}"

    drafts_updated = [
        d for d in drafts if (parse_dt(d.get("updated_at", "")) or dt.datetime.min.replace(tzinfo=dt.timezone.utc)) >= horizon
    ]
    prs_updated = [
        p for p in prs if (parse_dt(p.get("updated_at", "")) or dt.datetime.min.replace(tzinfo=dt.timezone.utc)) >= horizon
    ]
    issues_updated = [
        i for i in issues if (parse_dt(i.get("updated_at", "")) or dt.datetime.min.replace(tzinfo=dt.timezone.utc)) >= horizon
    ]

    candidates = backlog.get("candidates", [])

    lines: list[str] = []
    lines.append(f"# OAuth WG Weekly Digest - {week_id}")
    lines.append("")
    lines.append(f"Window: `{horizon.date().isoformat()}` to `{now.date().isoformat()}`")
    lines.append(f"Generated at: `{now.strftime('%Y-%m-%dT%H:%M:%SZ')}`")
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
                f"| `{d.get('name', '')}` | {d.get('rev', '')} | {d.get('updated_at', '')} | {states} |"
            )
    lines.append("")

    lines.append("## Top Deep-Dive Candidates")
    lines.append("")
    if not candidates:
        lines.append("- No scored candidates available.")
    else:
        lines.append("| Rank | Draft | Score | Reasons |")
        lines.append("|---:|---|---:|---|")
        for i, c in enumerate(candidates[:10], start=1):
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
                f"- `{pr.get('repo_full_name', '')}#{pr.get('number', '')}` {pr.get('title', '')} ({pr.get('updated_at', '')})"
            )
    lines.append("")

    out_path = root_dir / "reports" / "weekly" / f"{week_id}.md"
    write_text(out_path, "\n".join(lines) + "\n")
    print(f"weekly report written: {out_path}")


if __name__ == "__main__":
    main()
