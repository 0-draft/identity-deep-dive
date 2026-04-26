#!/usr/bin/env python3
"""Render daily or weekly markdown reports from normalized state."""
from __future__ import annotations

import argparse
import datetime as dt

from _common import ROOT, read_json, write_text


def render(state: dict, candidates: dict, mode: str) -> str:
    today = dt.date.today().isoformat()
    title = "Daily Report" if mode == "daily" else "Weekly Digest"
    lines = [f"# {title} ({today})", "", f"Generated at: {state.get('generated_at', '')}", ""]

    repos = state.get("github_repos", [])
    lines.append(f"## Tracked repositories ({len(repos)})")
    lines.append("")
    for r in sorted(repos, key=lambda x: x.get("pushed_at", ""), reverse=True):
        lines.append(f"- `{r.get('repo', '')}` pushed_at={r.get('pushed_at', '')}")
    lines.append("")

    ranked = candidates.get("candidates", [])
    lines.append("## Top Deep-Dive Candidates")
    lines.append("")
    if not ranked:
        lines.append("- No candidates above threshold.")
    else:
        for c in ranked[:10]:
            lines.append(f"- [{c.get('score', 0)}] {c.get('title', '')}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily", "weekly"], default="daily")
    args = parser.parse_args()

    state = read_json(ROOT / "data" / "normalized" / "state.json")
    candidates = read_json(ROOT / "data" / "normalized" / "candidates.json")

    body = render(state, candidates, args.mode)
    if args.mode == "daily":
        out = ROOT / "reports" / "daily" / f"{dt.date.today().isoformat()}.md"
    else:
        y, w, _ = dt.date.today().isocalendar()
        out = ROOT / "reports" / "weekly" / f"{y}-W{w:02d}.md"
    write_text(out, body + "\n")
    print(f"report-{args.mode}: {out}")


if __name__ == "__main__":
    main()
