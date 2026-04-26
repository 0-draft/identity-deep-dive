#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from lib import read_json, utc_now_iso, utc_today


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate weekly markdown summary")
    p.add_argument("--end-date", help="End date in YYYY-MM-DD (default: UTC today)")
    p.add_argument("--in-root", default="data/normalized")
    p.add_argument("--out-root", default="reports/weekly")
    return p.parse_args()


def iso_week_id(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def main() -> None:
    args = parse_args()
    end_date = date.fromisoformat(args.end_date) if args.end_date else utc_today()
    start_date = end_date - timedelta(days=6)

    in_root = Path(args.in_root)
    files = []
    for i in range(7):
        d = start_date + timedelta(days=i)
        f = in_root / f"scored-{d.isoformat()}.json"
        if f.exists():
            files.append((d, f))

    if not files:
        print("No scored snapshots found in this weekly window.")
        return

    appearances = defaultdict(int)
    score_sum = defaultdict(float)
    last_repo = {}

    top_n = None
    for d, f in files:
        scored = read_json(f)
        repos = scored.get("repos", [])
        if top_n is None:
            top_n = int(scored.get("settings", {}).get("top_n", 12))

        for r in repos[: int(top_n or 12)]:
            full = r["full_name"]
            appearances[full] += 1
            score_sum[full] += float(r.get("score", 0.0))
            last_repo[full] = r

    rows = []
    for full, cnt in appearances.items():
        avg = score_sum[full] / cnt
        r = last_repo[full]
        rows.append(
            {
                "full_name": full,
                "count": cnt,
                "avg_score": avg,
                "latest_score": float(r.get("score", 0.0)),
                "html_url": r.get("html_url"),
                "category": r.get("category"),
            }
        )

    rows.sort(key=lambda x: (-x["count"], -x["avg_score"], x["full_name"]))

    week_id = iso_week_id(end_date)
    lines: list[str] = []
    lines.append(f"# OpenID Radar Weekly - {week_id}")
    lines.append("")
    lines.append(f"Window: `{start_date.isoformat()}` to `{end_date.isoformat()}`")
    lines.append(f"Generated at: `{utc_now_iso()}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Snapshot files in window: `{len(files)}`")
    lines.append(f"- Top list size per day: `{top_n or 12}`")
    lines.append("")
    lines.append("## Repositories Persistently in Top List")
    lines.append("")
    lines.append("| Repo | Appearances | Avg Score | Latest Score | Category |")
    lines.append("|---|---:|---:|---:|---|")
    for row in rows[:20]:
        lines.append(
            f"| [{row['full_name']}]({row['html_url']}) | {row['count']} | {row['avg_score']:.2f} | {row['latest_score']:.2f} | {row['category']} |"
        )

    lines.append("")
    lines.append("## Recommended Deep Dive Queue")
    lines.append("")
    for row in rows[:5]:
        lines.append(
            f"- `{row['full_name']}` (appearances={row['count']}, avg_score={row['avg_score']:.2f})"
        )

    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    out_file = out_root / f"{week_id}.md"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Weekly report written: {out_file}")


if __name__ == "__main__":
    main()
