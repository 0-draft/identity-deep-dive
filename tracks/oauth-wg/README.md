# OAuth WG Deep Dive

Continuous monitoring and deep-dive workspace for the IETF OAuth WG (https://github.com/oauth-wg).

Pipeline: collect (GitHub via `gh` + Datatracker + Mailarchive) → normalize → score → daily/weekly Markdown.

## Repository Layout

```text
config/                Source/scoring configuration (YAML, JSON aliases)
scripts/               Collection / normalization / scoring / report scripts
data/snapshots/        Per-collection raw snapshots
data/normalized/       Latest normalized JSON
data/history/          Pointer to the latest snapshot directory
reports/daily/         Daily Markdown reports
reports/weekly/        Weekly Markdown digests
deep-dives/            Deep-dive topic scaffolds (see scripts/scaffold_topic.sh)
```

## Prerequisites

- `gh` (GitHub CLI) on PATH and `gh auth status` passing
- `python3`, `curl`

## Local Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make update     # collect + normalize + score + daily report
make weekly     # collect + normalize + score + weekly digest
```

Generated outputs:

- `data/snapshots/<UTC timestamp>/{datatracker,github,mailarchive}/...`
- `data/normalized/{drafts,repos,events,prs,issues,mailarchive,metadata,backlog}.json`
- `reports/daily/<YYYY-MM-DD>.md`, `reports/weekly/<YYYY>-W<NN>.md`
- `deep-dives/_backlog.md`

## Automation

Driven from the repo-root `.github/workflows/{daily-update,weekly-digest}.yml`. The `gh` CLI is authenticated via `GH_TOKEN`.

## Notes

- Scoring weights (lifecycle states, recency, repo activity) live in `config/scoring.yaml`.
- Repo→draft alias mapping lives in `config/draft_aliases.json` and is auto-extended for repos following `oauth-*` / `draft-ietf-oauth-*` naming.
