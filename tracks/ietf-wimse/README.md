# IETF WIMSE Deep Dive

Automated monitoring and deep-dive workspace for the IETF WIMSE working group.

## Goals

- Continuously collect the latest WIMSE signals from primary sources.
- Detect meaningful changes (draft revisions, new related drafts, meeting artifacts, mailing-list trends).
- Prioritize deep-dive candidates with reproducible scoring.
- Maintain a hands-on lab backlog tied to real WG movement.

## Data Sources

- Datatracker WG pages: documents, meetings, history.
- IETF mail archive (`wimse` list).
- GitHub repositories under `ietf-wg-wimse`.

All source endpoints and tracked repositories are configured in `config/sources.yaml`.

## Repository Layout

- `config/`: source and scoring configuration.
- `data/raw/`: raw fetch artifacts by date.
- `data/normalized/`: latest normalized source outputs and merged state.
- `data/snapshots/`: daily state snapshots.
- `reports/daily/`: generated daily markdown reports.
- `reports/weekly/`: generated weekly markdown reports.
- `backlog/candidate-queue.md`: scored deep-dive candidate queue.
- `deep-dives/`: manually curated deep-dive notes (scaffold from `../../templates/deep-dive/`).
- `scripts/`: data collection, normalization, scoring, and report generation.

## Local Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make update
```

`make update` runs:

1. Source collectors
2. State normalization
3. Candidate scoring
4. Daily report rendering

Useful targets:

- `make collect`
- `make normalize`
- `make score`
- `make report-daily`
- `make report-weekly`
- `make weekly`

## Automation

Driven from the repo-root `.github/workflows/{daily-update,weekly-digest}.yml`. Both workflows commit generated outputs when changed.

## Notes

- Generated files are intentionally committed for historical traceability.
- Scoring logic is intentionally simple and transparent; tune weights in `config/scoring.yaml`.
