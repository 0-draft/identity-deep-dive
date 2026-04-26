# Runbook

## Daily Local Run

```bash
./scripts/run_daily.sh
```

## Manual Snapshot Only

```bash
./scripts/collect_all.sh
./scripts/normalize.py
./scripts/score.py
```

## Manual Deep Dive Topic Scaffold

```bash
./scripts/scaffold_topic.sh draft-ietf-oauth-v2-1
```

## GitHub Actions

- `Collect OAuth WG Signals`:
  - cron: every 6 hours
  - Collection + normalization + scoring
- `Build Daily OAuth WG Report`:
  - cron: daily
  - Collection + report generation
- `Scaffold Deep Dive Topic`:
  - Manual execution, input: `draft_name`

## Failure Handling

- GitHub API rate limit:
  - Retry on next scheduled run
  - Manually trigger `workflow_dispatch` if needed
- Datatracker temporary failure:
  - Tolerate missing raw data; keep existing normalized data
- Mailarchive failure:
  - Continue with empty mail items in the report
