# OpenID Deep Dive

A research repository for continuously tracking public activity on `openid` (https://github.com/openid)
and mechanically extracting "topics worth digging into right now."

## Purpose

- Collect changes from key OpenID Foundation repositories on a daily basis
- Normalize collected data and assign priority scores
- Auto-generate daily/weekly reports
- Continuously surface candidates for Deep Dive investigation

## Directory Structure

- `config/watchlist.yaml`: Priority-watch repositories
- `config/scoring.yaml`: Scoring rules
- `scripts/`: Collection, formatting, scoring, and report generation
- `data/raw/YYYY-MM-DD/`: Raw GitHub API data
- `data/normalized/`: Normalized data and scoring results
- `reports/daily/`: Daily reports
- `reports/weekly/`: Weekly reports
- `deep-dives/`: Manual investigation notes and templates
- `.github/workflows/`: Automated update workflows

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

Having a `GITHUB_TOKEN` (or `GH_TOKEN`) helps avoid API rate limits.

```bash
export GITHUB_TOKEN=ghp_xxx
```

It works without a token, but when GitHub API rate limits are hit, some metrics may be missing and warnings will appear in the report's `Notes` section.

## Usage

```bash
make update     # collect + normalize + score + daily report
make weekly     # collect + normalize + score + weekly report
```

Backfill a specific date by invoking the underlying scripts directly:

```bash
python scripts/fetch_openid.py --date 2026-04-05
python scripts/normalize.py --date 2026-04-05
python scripts/score.py --date 2026-04-05
python scripts/generate_daily_report.py --date 2026-04-05
```

## Automated Updates

Driven from the repo-root `.github/workflows/{daily-update,weekly-digest}.yml`. Both commit changes when present.

## Deep Dive Workflow

Copy `deep-dives/_template/` to start a new topic.

```bash
cp -R deep-dives/_template deep-dives/<topic-name>
```

The workflow involves filling in `context.md` / `spec-notes.md` / `interop-checklist.md` / `hands-on-log.md`.
