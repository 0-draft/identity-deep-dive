# OpenID Deep Dive

Continuous monitoring and deep-dive workspace for the OpenID Foundation org (`github.com/openid`).

## Purpose

- Track all public OpenID Foundation repositories (specs + reference implementations).
- Surface deep-dive candidates ranked by activity, recency, and watchlist weighting.
- Generate daily and weekly Markdown reports for review.

## Sources

Configured in `config/sources.yaml` (priority repos with weights). All other public repos under the `openid` GitHub org are also collected.

- GitHub `openid` org (repos, open PRs, open issues, merged PRs in last 30 days) — REST API via `requests`

## Layout

```text
config/                              sources.yaml + scoring.yaml
data/raw/<YYYY-MM-DD>/github.json    Raw GitHub API JSON (latest only — pruned)
data/normalized/github.json          Per-source normalized (latest collect)
data/normalized/state.json           Merged state (input to score)
data/normalized/candidates.json      Scored repos (input to report)
data/snapshots/<YYYY-MM-DD>/         state.json + candidates.json (last 7 for weekly digest)
reports/daily/<YYYY-MM-DD>.md        Latest daily report
reports/weekly/<YYYY>-W<NN>.md       Latest weekly digest
deep-dives/_template/                Deep-dive scaffold to copy
deep-dives/<topic>/                  Investigation notes
scripts/                             _common.py + collect_github.py / normalize.py / score.py / report.py
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
python scripts/collect_github.py --date 2026-04-05
python scripts/normalize.py      --date 2026-04-05
python scripts/score.py          --date 2026-04-05
python scripts/report.py --mode daily --date 2026-04-05
```

## Automation

Driven by repo-root `.github/workflows/{daily-update,weekly-digest}.yml` (matrix over all tracks).

## Notes

- Scoring weights (recency window, threshold buckets, watchlist bonus) live in `config/scoring.yaml`.
- Retention: `make prune` keeps only the latest report and raw snapshot, plus the last 7 `data/snapshots/<date>/` directories (needed for the weekly digest's 7-day lookback).
