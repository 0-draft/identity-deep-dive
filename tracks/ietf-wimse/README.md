# IETF WIMSE Deep Dive

Continuous monitoring and deep-dive workspace for the IETF WIMSE working group (Workload Identity in Multi-System Environments).

## Purpose

- Track WIMSE drafts, related specifications, and working-group activity.
- Surface deep-dive candidates ranked by lifecycle state, recency, and mailing-list signal.
- Generate daily and weekly Markdown reports for review.

## Sources

Configured in `config/sources.yaml`:

- IETF Datatracker (WG documents, meetings, history) — HTML scrape
- IETF Mail Archive (`mailarchive.ietf.org/arch/browse/wimse/`) — HTML scrape
- GitHub repos under `ietf-wg-wimse/` — REST API

## Layout

```text
config/                      sources.yaml + scoring.yaml
data/raw/<YYYY-MM-DD>/       Per-source audit JSON (latest only — pruned)
data/normalized/             datatracker.json / mailarchive.json / github.json /
                             state.json / candidates.json
data/snapshots/<YYYY-MM-DD>/ Snapshot of normalized state
reports/daily/<YYYY-MM-DD>.md     Latest daily report
reports/weekly/<YYYY>-W<NN>.md    Latest weekly digest
deep-dives/_backlog.md       Scored deep-dive candidate queue
deep-dives/<topic>/          Investigation notes
scripts/                     _common.py + collect_*.py / normalize.py / score.py / report.py
```

## Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make update     # collect + normalize + score + report-daily + prune
make weekly     # collect + normalize + score + report-weekly + prune
```

Set `GITHUB_TOKEN` (or `GH_TOKEN`) to avoid GitHub API rate limits.

## Automation

Driven by repo-root `.github/workflows/{daily-update,weekly-digest}.yml` (matrix over all tracks).

## Notes

- Scoring weights live in `config/scoring.yaml` (`recency_days`, `weights`, `priority_keywords`).
- Retention: `make prune` keeps only the latest report and snapshot. For older state use git history.
