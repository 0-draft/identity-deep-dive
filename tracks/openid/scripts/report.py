#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from collections import defaultdict
from pathlib import Path
from typing import Any

from _common import ROOT, iso_now, read_json, today_utc, write_text


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Render OpenID markdown reports")
    p.add_argument("--mode", choices=["daily", "weekly"], required=True)
    p.add_argument("--date", help="Snapshot date (default: UTC today)")
    return p.parse_args()


def find_previous_snapshot(snapshot_date: dt.date) -> Path | None:
    root = ROOT / "data" / "snapshots"
    if not root.exists():
        return None
    candidates = sorted(
        p / "candidates.json"
        for p in root.iterdir()
        if p.is_dir() and p.name < snapshot_date.isoformat() and (p / "candidates.json").exists()
    )
    return candidates[-1] if candidates else None


def fmt_rank_delta(curr_rank: int, prev_rank: int | None) -> str:
    if prev_rank is None:
        return "new"
    delta = prev_rank - curr_rank
    if delta > 0:
        return f"up {delta}"
    if delta < 0:
        return f"down {abs(delta)}"
    return "same"


def render_daily(state: dict[str, Any], candidates: dict[str, Any], snapshot_date: dt.date) -> str:
    repos = candidates.get("candidates", [])
    settings = candidates.get("settings", {})
    top_n = int(settings.get("top_n", 12))
    threshold = float(settings.get("deep_dive_threshold", 8.0))

    stats = state.get("stats", {})
    open_prs_total = int(state.get("github_search_totals", {}).get("open_prs", 0))
    open_issues_total = int(state.get("github_search_totals", {}).get("open_issues", 0))
    fetch_errors = state.get("fetch_errors", {})

    top = repos[:top_n]
    deep_dives = [r for r in repos if float(r.get("score", 0)) >= threshold][:8]
    fresh_pushes = [r for r in repos if (r.get("days_since_push") or 99999) <= 3][:12]

    prev_path = find_previous_snapshot(snapshot_date)
    prev_map: dict[str, dict[str, Any]] = {}
    if prev_path:
        prev_map = {r["full_name"]: r for r in read_json(prev_path).get("candidates", [])}

    lines: list[str] = []
    lines.append(f"# OpenID Radar Daily - {snapshot_date.isoformat()}")
    lines.append("")
    lines.append(f"Generated at: `{iso_now()}`")
    lines.append("")
    lines.append("## Snapshot")
    lines.append("")
    lines.append(f"- Public repositories: `{stats.get('repos', 0)}`")
    lines.append(f"- Active (push <= 30 days): `{stats.get('active_30d', 0)}`")
    lines.append(f"- Active (push <= 90 days): `{stats.get('active_90d', 0)}`")
    lines.append(f"- Archived repositories: `{stats.get('archived', 0)}`")
    lines.append(f"- Open PRs (org total): `{open_prs_total}`")
    lines.append(f"- Open issues (org total): `{open_issues_total}`")
    lines.append("")
    lines.append("## Top Focus")
    lines.append("")
    lines.append("| Rank | Repo | Score | Category | Push Age | Open PRs | Open Issues | Trend |")
    lines.append("|---:|---|---:|---|---:|---:|---:|---|")
    for r in top:
        prev = prev_map.get(r["full_name"])
        trend = fmt_rank_delta(r["rank"], prev.get("rank") if prev else None)
        lines.append(
            f"| {r['rank']} | [{r['full_name']}]({r['html_url']}) | {r['score']:.2f} | "
            f"{r['category']} | {r.get('days_since_push', 'n/a')}d | "
            f"{r.get('open_prs', 0)} | {r.get('open_issues', 0)} | {trend} |"
        )

    lines.append("")
    lines.append("## Deep Dive Candidates")
    lines.append("")
    if deep_dives:
        for r in deep_dives:
            lines.append(
                f"- `{r['full_name']}` score={r['score']:.2f} / "
                f"open_prs={r.get('open_prs', 0)} / "
                f"open_issues={r.get('open_issues', 0)} / "
                f"days_since_push={r.get('days_since_push', 'n/a')}"
            )
    else:
        lines.append("- No candidates above threshold today.")

    lines.append("")
    lines.append("## Fresh Pushes (<= 3 days)")
    lines.append("")
    if fresh_pushes:
        for r in fresh_pushes:
            lines.append(f"- `{r['full_name']}` pushed_at={r.get('pushed_at') or 'n/a'}")
    else:
        lines.append("- No recent pushes.")

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    if prev_path:
        lines.append(f"- Compared with previous snapshot: `{prev_path.parent.name}`")
    else:
        lines.append("- Previous snapshot not found; trend is partial.")
    for k, v in (fetch_errors or {}).items():
        if v:
            lines.append(f"- Warning: `{k}` fetch error: `{v}`")

    return "\n".join(lines) + "\n"


def render_weekly(snapshot_date: dt.date) -> tuple[str, str]:
    start_date = snapshot_date - dt.timedelta(days=6)
    snapshots: list[tuple[dt.date, Path]] = []
    for i in range(7):
        d = start_date + dt.timedelta(days=i)
        path = ROOT / "data" / "snapshots" / d.isoformat() / "candidates.json"
        if path.exists():
            snapshots.append((d, path))

    appearances: dict[str, int] = defaultdict(int)
    score_sum: dict[str, float] = defaultdict(float)
    last_repo: dict[str, dict[str, Any]] = {}
    top_n = 12

    for _, path in snapshots:
        data = read_json(path)
        top_n = int(data.get("settings", {}).get("top_n", 12))
        for r in data.get("candidates", [])[:top_n]:
            full = r["full_name"]
            appearances[full] += 1
            score_sum[full] += float(r.get("score", 0.0))
            last_repo[full] = r

    rows = []
    for full, cnt in appearances.items():
        r = last_repo[full]
        rows.append(
            {
                "full_name": full,
                "count": cnt,
                "avg_score": score_sum[full] / cnt,
                "latest_score": float(r.get("score", 0.0)),
                "html_url": r.get("html_url"),
                "category": r.get("category"),
            }
        )
    rows.sort(key=lambda x: (-x["count"], -x["avg_score"], x["full_name"]))

    iso_year, iso_week, _ = snapshot_date.isocalendar()
    week_id = f"{iso_year}-W{iso_week:02d}"

    lines: list[str] = []
    lines.append(f"# OpenID Radar Weekly - {week_id}")
    lines.append("")
    lines.append(f"Window: `{start_date.isoformat()}` to `{snapshot_date.isoformat()}`")
    lines.append(f"Generated at: `{iso_now()}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Snapshot files in window: `{len(snapshots)}`")
    lines.append(f"- Top list size per day: `{top_n}`")
    lines.append("")
    lines.append("## Repositories Persistently in Top List")
    lines.append("")
    lines.append("| Repo | Appearances | Avg Score | Latest Score | Category |")
    lines.append("|---|---:|---:|---:|---|")
    for row in rows[:20]:
        lines.append(
            f"| [{row['full_name']}]({row['html_url']}) | {row['count']} | "
            f"{row['avg_score']:.2f} | {row['latest_score']:.2f} | {row['category']} |"
        )

    lines.append("")
    lines.append("## Recommended Deep Dive Queue")
    lines.append("")
    for row in rows[:5]:
        lines.append(
            f"- `{row['full_name']}` (appearances={row['count']}, avg_score={row['avg_score']:.2f})"
        )

    return "\n".join(lines) + "\n", week_id


def main() -> None:
    args = parse_args()
    snapshot_date = dt.date.fromisoformat(args.date) if args.date else today_utc()

    if args.mode == "daily":
        state = read_json(ROOT / "data" / "normalized" / "state.json")
        candidates = read_json(ROOT / "data" / "normalized" / "candidates.json")
        out = render_daily(state, candidates, snapshot_date)
        out_path = ROOT / "reports" / "daily" / f"{snapshot_date.isoformat()}.md"
        write_text(out_path, out)
        print(f"report-daily: {out_path}")
        return

    out, week_id = render_weekly(snapshot_date)
    out_path = ROOT / "reports" / "weekly" / f"{week_id}.md"
    write_text(out_path, out)
    print(f"report-weekly: {out_path}")


if __name__ == "__main__":
    main()
