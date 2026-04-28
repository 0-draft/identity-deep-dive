# Runbook

## Daily Local Run

```bash
make update
```

## Manual Pipeline Stages

```bash
make collect       # collect_datatracker.py + collect_mailarchive.py + collect_github.py
make normalize     # merge into data/normalized/state.json + daily snapshot
make score         # write data/normalized/candidates.json
make report-daily  # render reports/daily/<date>.md + deep-dives/_backlog.md
```

## Manual Deep Dive Topic Scaffold

```bash
./scripts/scaffold_topic.sh draft-ietf-oauth-v2-1
```

## GitHub Actions

Repo-root workflows handle scheduling (no per-track workflows):

- `.github/workflows/daily-update.yml` — 06:00 UTC matrix run, executes `make update` for each track and commits the result.
- `.github/workflows/weekly-digest.yml` — Mondays 08:00 UTC matrix run, executes `make weekly`.

## Failure Handling

- GitHub API rate limit:
  - `_common._request` already retries 429/5xx with `Retry-After`; persistent failures will surface as a non-zero exit and re-run on the next schedule.
  - Set `GITHUB_TOKEN` (or `GH_TOKEN`) in the environment to lift the unauthenticated rate limit.
- Datatracker temporary failure:
  - Tolerate missing raw data; keep existing normalized data and re-run later.
- Mailarchive failure:
  - Continue with empty mail items in the report.
