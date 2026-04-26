# Architecture

## Goal

Make it possible to track changes in the OAuth WG on a daily basis.

1. Periodically collect raw data
2. Normalize to machine-readable format
3. Prioritize by state transitions and activity volume
4. Generate daily Markdown reports

## Data Flow

1. `scripts/collect_all.sh`
   - GitHub: org repos / org events / PR / issue search
   - Datatracker: WG metadata / draft list / state taxonomy
   - Mailarchive: oauth list index
2. `scripts/normalize.py`
   - Generate monitoring-oriented JSON from raw data
3. `scripts/score.py`
   - Assign a score to each draft and build the backlog
4. `scripts/build_daily_report.py`
   - Generate daily report and `deep-dives/_backlog.md`

## Snapshot Policy

- Storage: `data/snapshots/<UTC timestamp>/`
- Timestamp format: `YYYY-MM-DDTHHMMSSZ`
- Latest is recorded in `data/history/latest_snapshot.txt`

## Non-Goals

- Build/test automation for OAuth implementation code itself
- Automated publishing integration with posting platforms
