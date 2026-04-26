# OpenID Deep Dive

Continuous monitoring and deep-dive workspace for the OpenID Foundation org (`github.com/openid`).

## Purpose

- Track all public OpenID Foundation repositories (specs + reference implementations).
- Surface deep-dive candidates ranked by activity, recency, and watchlist weighting.
- Generate daily and weekly Markdown reports for review.

## Sources

Configured in `config/watchlist.yaml` (priority repos with weights). All other public repos under the `openid` GitHub org are also collected.

- GitHub `openid` org (repos, open PRs, open issues, merged PRs in last 30 days) — REST API via stdlib `urllib`

## Layout

```text
config/                            watchlist.yaml + scoring.yaml
data/raw/<YYYY-MM-DD>/             Raw GitHub API JSON (latest only — pruned)
data/normalized/latest.json        Latest snapshot pointer (always present)
data/normalized/repos-<date>.json  Normalized per-day (last 7 kept for weekly digest)
data/normalized/scored-<date>.json Scored per-day (last 7 kept)
data/normalized/top-<date>.json    Top N per-day (last 7 kept)
reports/daily/<YYYY-MM-DD>.md      Latest daily report
reports/weekly/<YYYY>-W<NN>.md     Latest weekly digest
deep-dives/_template/              Deep-dive scaffold to copy
deep-dives/<topic>/                Investigation notes
scripts/                           _common.py + fetch_openid.py / normalize.py / score.py / report.py
```

## Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make update     # collect + normalize + score + report-daily + prune
make weekly     # collect + normalize + score + report-weekly + prune
```

Set `GITHUB_TOKEN` (or `GH_TOKEN`) to avoid GitHub API rate limits. Without a token, rate-limited metrics will appear as warnings in the report's Notes section.

Backfill a specific date by invoking scripts directly:

```bash
python scripts/fetch_openid.py --date 2026-04-05
python scripts/normalize.py     --date 2026-04-05
python scripts/score.py         --date 2026-04-05
python scripts/report.py --mode daily --date 2026-04-05
```

## Automation

Driven by repo-root `.github/workflows/{daily-update,weekly-digest}.yml` (matrix over all tracks).

## Notes

- Scoring weights (recency window, threshold buckets, watchlist bonus) live in `config/scoring.yaml`.
- Retention: `make prune` keeps only the latest report and snapshot, plus the last 7 dated `data/normalized/<prefix>-<date>.json` files (needed for the weekly digest).
