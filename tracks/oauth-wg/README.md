# OAuth WG Deep Dive

Continuous monitoring and deep-dive workspace for the IETF OAuth working group (`oauth-wg` on GitHub, `oauth` on Datatracker).

## Purpose

- Track all OAuth WG drafts, repository activity, and discussion lists.
- Surface deep-dive candidates ranked by lifecycle state, recency, and repo/issue activity.
- Generate daily and weekly Markdown reports for review.

## Sources

- IETF Datatracker (group, drafts, state taxonomy) — REST API + HTML
- GitHub `oauth-wg` org (repos, events, PRs, issues) — `gh` CLI
- IETF Mail Archive (`oauth` list) — HTML scrape

Repo→draft alias mapping lives in `config/draft_aliases.json`; auto-extended for `oauth-*` / `draft-ietf-oauth-*` names.

## Layout

```text
config/                      scoring.yaml + draft_aliases.json
data/snapshots/<UTC ts>/     Per-collection raw snapshots (latest only — pruned)
data/normalized/             drafts.json / repos.json / events.json / prs.json /
                             issues.json / mailarchive.json / metadata.json / backlog.json
data/history/                Pointer file: latest snapshot timestamp
reports/daily/<YYYY-MM-DD>.md     Latest daily report
reports/weekly/<YYYY>-W<NN>.md    Latest weekly digest
deep-dives/_backlog.md       Scored deep-dive candidate queue
deep-dives/<topic>/          Investigation notes (scaffold via scripts/scaffold_topic.sh)
scripts/                     collect_*.sh / normalize.py / score.py / report.py
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

- `gh` (GitHub CLI) on `PATH`, with `gh auth status` passing (CI uses `GH_TOKEN`).
- `python3`, `curl`.

## Automation

Driven by repo-root `.github/workflows/{daily-update,weekly-digest}.yml` (matrix over all tracks). `GH_TOKEN` is provided to `gh` in CI.

## Notes

- Scoring weights (lifecycle states, recency window, repo activity, open-issue thresholds) live in `config/scoring.yaml`.
- Retention: `make prune` keeps only the latest report and snapshot. For older state use git history.
