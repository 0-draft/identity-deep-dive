# <Track Name> Deep Dive

Automated monitoring and deep-dive workspace for **<Track Name>**.

## Goals

- Continuously collect the latest signals from primary sources.
- Detect meaningful changes (draft revisions, new specs, repo activity, mailing-list trends).
- Prioritize deep-dive candidates with reproducible scoring.
- Maintain a hands-on backlog tied to real working-group movement.

## Data Sources

- <!-- Add your sources here -->

All source endpoints and tracked repositories are configured in `config/sources.yaml`.

## Repository Layout

- `config/`: Source and scoring configuration.
- `data/raw/`: Raw fetch artifacts by date.
- `data/normalized/`: Latest normalized outputs and merged state.
- `data/snapshots/`: Daily state snapshots.
- `reports/daily/`: Generated daily markdown reports.
- `reports/weekly/`: Generated weekly markdown reports.
- `deep-dives/`: Investigation notes (use `../../templates/deep-dive/` as scaffold).
- `scripts/`: Data collection, normalization, scoring, and report generation.

## Local Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
make update
```

## Automation

Configure GitHub Actions in the top-level `.github/workflows/` directory.
