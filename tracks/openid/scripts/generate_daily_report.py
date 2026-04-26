#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib import read_json, utc_now_iso, utc_today


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate daily markdown report")
    p.add_argument("--date", help="Snapshot date in YYYY-MM-DD (default: UTC today)")
    p.add_argument("--in-root", default="data/normalized")
    p.add_argument("--out-root", default="reports/daily")
    return p.parse_args()


def find_prev_scored(root: Path, snapshot_date: str) -> Path | None:
    files = sorted(root.glob("scored-*.json"))
    prev = [f for f in files if f.stem.replace("scored-", "") < snapshot_date]
    return prev[-1] if prev else None


def build_rank_map(repos: list[dict]) -> dict[str, dict]:
    return {r["full_name"]: r for r in repos}


def fmt_rank_delta(curr_rank: int, prev_rank: int | None) -> str:
    if prev_rank is None:
        return "new"
    delta = prev_rank - curr_rank
    if delta > 0:
        return f"up {delta}"
    if delta < 0:
        return f"down {abs(delta)}"
    return "same"


def main() -> None:
    args = parse_args()
    snapshot_date = args.date or utc_today().isoformat()

    in_root = Path(args.in_root)
    scored = read_json(in_root / f"scored-{snapshot_date}.json")
    repos = scored["repos"]

    prev_file = find_prev_scored(in_root, snapshot_date)
    prev_map = {}
    if prev_file:
        prev_map = build_rank_map(read_json(prev_file).get("repos", []))

    settings = scored.get("settings", {})
    top_n = int(settings.get("top_n", 12))
    threshold = float(settings.get("deep_dive_threshold", 8.0))

    total = len(repos)
    active_30 = sum(1 for r in repos if r.get("days_since_push", 99999) <= 30)
    active_90 = sum(1 for r in repos if r.get("days_since_push", 99999) <= 90)
    archived = sum(1 for r in repos if r.get("archived", False))
    source = scored.get("source", {})
    open_prs_total = int(source.get("open_prs_total", sum(int(r.get("open_prs", 0)) for r in repos)))
    open_issues_total = int(source.get("open_issues_total", sum(int(r.get("open_issues", 0)) for r in repos)))
    fetch_errors = source.get("fetch_errors", {})

    top = repos[:top_n]
    deep_dives = [r for r in repos if float(r.get("score", 0)) >= threshold][:8]
    fresh_pushes = [r for r in repos if r.get("days_since_push", 99999) <= 3][:12]

    lines: list[str] = []
    lines.append(f"# OpenID Radar Daily - {snapshot_date}")
    lines.append("")
    lines.append(f"Generated at: `{utc_now_iso()}`")
    lines.append("")
    lines.append("## Snapshot")
    lines.append("")
    lines.append(f"- Public repositories: `{total}`")
    lines.append(f"- Active (push <= 30 days): `{active_30}`")
    lines.append(f"- Active (push <= 90 days): `{active_90}`")
    lines.append(f"- Archived repositories: `{archived}`")
    lines.append(f"- Open PRs (org total): `{open_prs_total}`")
    lines.append(f"- Open issues (org total): `{open_issues_total}`")
    lines.append("")
    lines.append("## Top Focus")
    lines.append("")
    lines.append("| Rank | Repo | Score | Category | Push Age | Open PRs | Open Issues | Trend |")
    lines.append("|---:|---|---:|---|---:|---:|---:|---|")

    for r in top:
        full = r["full_name"]
        prev = prev_map.get(full)
        trend = fmt_rank_delta(r["rank"], prev.get("rank") if prev else None)
        lines.append(
            f"| {r['rank']} | [{full}]({r['html_url']}) | {r['score']:.2f} | {r['category']} | {r['days_since_push']}d | {r['open_prs']} | {r['open_issues']} | {trend} |"
        )

    lines.append("")
    lines.append("## Deep Dive Candidates")
    lines.append("")
    if deep_dives:
        for r in deep_dives:
            lines.append(
                f"- `{r['full_name']}` score={r['score']:.2f} / open_prs={r['open_prs']} / open_issues={r['open_issues']} / days_since_push={r['days_since_push']}"
            )
    else:
        lines.append("- No candidates above threshold today.")

    lines.append("")
    lines.append("## Fresh Pushes (<= 3 days)")
    lines.append("")
    if fresh_pushes:
        for r in fresh_pushes:
            pushed_at = r.get("pushed_at") or "n/a"
            lines.append(f"- `{r['full_name']}` pushed_at={pushed_at}")
    else:
        lines.append("- No recent pushes.")

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    if prev_file:
        lines.append(f"- Compared with previous snapshot: `{prev_file.stem.replace('scored-', '')}`")
    else:
        lines.append("- Previous snapshot not found; trend is partial.")
    if fetch_errors:
        for k, v in fetch_errors.items():
            if v:
                lines.append(f"- Warning: `{k}` fetch error: `{v}`")

    out_dir = Path(args.out_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{snapshot_date}.md"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Daily report written: {out_file}")


if __name__ == "__main__":
    main()
