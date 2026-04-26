# &lt;Track Name&gt; Deep Dive

Automated monitoring and deep-dive workspace for **&lt;Track Name&gt;**.

## Goals

- Continuously collect the latest signals from primary sources.
- Detect meaningful changes (draft revisions, new specs, repo activity, mailing-list trends).
- Prioritize deep-dive candidates with reproducible scoring.
- Maintain a hands-on backlog tied to real working-group movement.

## Data Sources

- &lt;!-- Add your sources here --&gt;

All source endpoints and tracked repositories are configured in `config/sources.yaml`.

## Repository Layout

- `config/`: Source and scoring configuration.
- `data/raw/<YYYY-MM-DD>/<source>.json`: Raw fetch artifacts.
- `data/normalized/`: Merged state and scoring output.
- `reports/daily/<YYYY-MM-DD>.md` and `reports/weekly/<YYYY>-W<NN>.md`: Generated reports.
- `backlog/candidate-queue.md`: Scored deep-dive candidate queue.
- `deep-dives/`: Investigation notes (scaffold from `../../templates/deep-dive/`).
- `scripts/`: `_common.py` helpers + `collect.py` / `normalize.py` / `score.py` / `report.py`.

## Local Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make update     # collect + normalize + score + report-daily
make weekly     # collect + normalize + score + report-weekly
```

Individual stages: `make collect`, `make normalize`, `make score`, `make report-daily`, `make report-weekly`.

## Automation

The repo-root `.github/workflows/{daily-update,weekly-digest}.yml` files use a `matrix.track` list. Add this track's directory name to that list to wire it into CI.
