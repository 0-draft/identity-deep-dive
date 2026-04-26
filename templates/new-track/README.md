# &lt;Track Name&gt; Deep Dive

Automated monitoring and deep-dive workspace for **&lt;Track Name&gt;**.

## Purpose

- Continuously collect signals from primary sources.
- Detect meaningful changes (draft revisions, repo activity, mailing-list trends).
- Prioritize deep-dive candidates with reproducible scoring.
- Generate daily and weekly Markdown reports.

## Sources

Configured in `config/sources.yaml`. Add the upstream URLs and tracked repositories you want to watch.

## Layout

```text
config/                      sources.yaml + scoring.yaml
data/raw/<YYYY-MM-DD>/       Raw fetch artifacts (latest only — pruned)
data/normalized/             Merged state + scoring output
reports/daily/<YYYY-MM-DD>.md     Latest daily report (older pruned)
reports/weekly/<YYYY>-W<NN>.md    Latest weekly digest (older pruned)
deep-dives/_backlog.md       Scored deep-dive candidate queue
deep-dives/<topic>/          Investigation notes (scaffold from templates/deep-dive/)
scripts/                     _common.py + collect.py / normalize.py / score.py / report.py
```

## Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make update     # collect + normalize + score + report-daily + prune
make weekly     # collect + normalize + score + report-weekly + prune
```

Individual stages: `make collect`, `make normalize`, `make score`, `make report-daily`, `make report-weekly`, `make prune`.

## Automation

The repo-root `.github/workflows/{daily-update,weekly-digest}.yml` files run `make update` / `make weekly` per track via a `matrix.track` list. Add this track's directory name to that list to wire it into CI.

## Notes

- Retention policy: `make prune` (auto-invoked by `update` / `weekly`) keeps only the latest report and snapshot per category. Use git history for older state.
- Set `GITHUB_TOKEN` (or `GH_TOKEN`) to avoid rate limits on GitHub fetches.
