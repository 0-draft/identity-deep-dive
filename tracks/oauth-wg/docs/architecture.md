# Architecture

## Goal

Make it possible to track changes in the OAuth WG on a daily basis.

1. Periodically collect raw data
2. Normalize to machine-readable format
3. Prioritize by state transitions and activity volume
4. Generate daily Markdown reports

## Data Flow

1. `scripts/collect_datatracker.py` / `collect_mailarchive.py` / `collect_github.py`
   - GitHub: `oauth-wg` org repos / org events / PR + issue search (`_common.github_paginate`)
   - Datatracker: WG metadata / draft list / state taxonomy + documents/meetings HTML
   - Mailarchive: `oauth` list index
   - Each writes `data/raw/<YYYY-MM-DD>/<source>.json` and `data/normalized/<source>.json`
2. `scripts/normalize.py`
   - Merges per-source normalized files into `data/normalized/state.json` plus a daily snapshot under `data/snapshots/<YYYY-MM-DD>/state.json`
3. `scripts/score.py`
   - Reads `state.json`, applies the lifecycle/recency/activity/open-issue formula from `config/scoring.yaml`, writes `data/normalized/candidates.json` and a snapshot copy under `data/snapshots/<YYYY-MM-DD>/`
4. `scripts/report.py --mode {daily,weekly}`
   - Daily: report + `deep-dives/_backlog.md`
   - Weekly: digest filtered to the last 7 days from `state.json`

## Snapshot Policy

- Storage: `data/snapshots/<YYYY-MM-DD>/{state,candidates}.json`
- Retention: `make prune` keeps the latest 7 daily snapshots (weekly digest lookback window)
- Raw audit copies: `data/raw/<YYYY-MM-DD>/`, latest day only

## Non-Goals

- Build/test automation for OAuth implementation code itself
- Automated publishing integration with posting platforms
