# OAuth WG Deep Dive

Continuous monitoring and deep-dive workspace for the IETF OAuth working group (`oauth-wg` on GitHub, `oauth` on Datatracker).

## Purpose

- Track all OAuth WG drafts, repository activity, and discussion lists.
- Surface deep-dive candidates ranked by lifecycle state, recency, and repo/issue activity.
- Generate daily and weekly Markdown reports for review.

## Sources

- IETF Datatracker (group, drafts, state taxonomy) — REST API + HTML
- GitHub `oauth-wg` org (repos, events, PRs, issues) — REST API
- IETF Mail Archive (`oauth` list) — HTML scrape

Source endpoints live in `config/sources.yaml`. Repo→draft alias mapping lives in `config/draft_aliases.json`; auto-extended for `oauth-*` / `draft-ietf-oauth-*` names.

## Layout

```text
config/                            sources.yaml + scoring.yaml + draft_aliases.json
data/raw/<YYYY-MM-DD>/             Per-day raw fetches (datatracker/github/mailarchive json)
data/normalized/                   datatracker.json / github.json / mailarchive.json /
                                   state.json / candidates.json
data/snapshots/<YYYY-MM-DD>/       Daily snapshot of state.json + candidates.json
reports/daily/<YYYY-MM-DD>.md      Latest daily report
reports/weekly/<YYYY>-W<NN>.md     Latest weekly digest
deep-dives/_backlog.md             Scored deep-dive candidate queue
deep-dives/<topic>/                Investigation notes (scaffold via scripts/scaffold_topic.sh)
scripts/                           _common.py + collect_*.py + normalize.py + score.py + report.py
```

## Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make update     # collect + normalize + score + report-daily + prune
make weekly     # collect + normalize + score + report-weekly + prune
```

Prerequisites:

- `python3` with the deps in `requirements.txt`.
- `GITHUB_TOKEN` or `GH_TOKEN` in env (for GitHub REST authentication and rate limit headroom).

## Automation

Driven by repo-root `.github/workflows/{daily-update,weekly-digest}.yml` (matrix over all tracks). `GH_TOKEN` is provided in CI.

## Notes

- Scoring weights (lifecycle states, recency window, repo activity, open-issue thresholds) live in `config/scoring.yaml`.
- Retention: `make prune` keeps only the latest report and snapshot. For older state use git history.
