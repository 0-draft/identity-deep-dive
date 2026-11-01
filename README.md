# Identity Deep Dive

A unified repository for continuously monitoring identity and security standards, detecting meaningful changes, and organizing deep-dive investigations into emerging topics.

## Tracked Domains

| Track                            | Scope                                          | Sources                           |
| -------------------------------- | ---------------------------------------------- | --------------------------------- |
| [IETF WIMSE](tracks/ietf-wimse/) | Workload Identity in Multi-System Environments | Datatracker, Mail Archive, GitHub |
| [OAuth WG](tracks/oauth-wg/)     | OAuth Working Group drafts and implementations | Datatracker, Mail Archive, GitHub |
| [OpenID](tracks/openid/)         | OpenID Foundation specifications and repos     | GitHub                            |

## How It Works

Each track follows the same pipeline:

```text
Collect  ->  Normalize  ->  Score  ->  Report  ->  Explain
  raw API       JSON         ranked      daily/weekly   Claude briefing
  snapshots     merge        backlog     markdown       + triage
```

1. **Collect** — Fetch raw data from configured sources (GitHub API, IETF Datatracker, mailing lists).
2. **Normalize** — Transform raw data into a consistent JSON schema per track.
3. **Score** — Rank items by lifecycle state, recency, and activity to surface what matters now.
4. **Report** — Generate daily and weekly markdown reports with prioritized tables.
5. **Explain** — In CI, find what is new since the last explained state (draft revisions, new drafts, mailing-list threads, PRs, repository activity), fetch the source material, and have Claude explain each item: a one-line headline, a summary grounded in the diff or message, a mermaid diagram of the mechanism, use cases, and links to related items in the other tracks. Claude also flags deep-dive candidates to move up or down: `candidates.json` and the site list raised candidates first, and a "Triage" section is appended to `deep-dives/_backlog.md`. The result lands in a "Briefing" section at the top of the daily report and in `data/normalized/insights.json` (a rolling seven-day window). See `scripts/insights/`.

## Repository Layout

```text
tracks/                     Per-domain monitoring pipelines
  ietf-wimse/                 IETF WIMSE working group
  oauth-wg/                   OAuth working group
  openid/                     OpenID Foundation
templates/                  Reusable templates
  new-track/                  Scaffold for adding a new track
  deep-dive/                  Deep-dive investigation template
  lab-report.md               Hands-on lab report template
scripts/                    Shared utilities
.github/workflows/          Unified automation
```

## Quick Start

### Run a single track

```bash
cd tracks/ietf-wimse
python3 -m venv .venv && source .venv/bin/activate
make install
make update        # collect + normalize + score + daily report
make weekly        # collect + normalize + score + weekly digest
```

Every track exposes the same `install` / `update` / `weekly` Makefile targets.

### Add a new track

```bash
cp -R templates/new-track tracks/<your-track-name>
# Edit tracks/<your-track-name>/config/ to point at your sources
# Implement or adapt the collection scripts
```

### Start a deep dive on a new topic

```bash
cp -R templates/deep-dive tracks/<track>/deep-dives/<topic-name>
# Fill in: context.md -> spec-notes.md -> interop-checklist.md -> hands-on-log.md
```

## Automation

Two repo-root workflows in `.github/workflows/` fan out across all tracks via a `matrix.track` list:

- `daily-update.yml` — every six hours. A read-only `collect` job per track runs `make install && make update`, stages what is new since the last explained state (`data/normalized/insights_baseline.json`), and has Claude explain it with read-only tools and structured output. A separate `publish` job, with no model in it, validates the result with `scripts/insights/apply.py`, commits per track and pushes. Without the `CLAUDE_CODE_OAUTH_TOKEN` secret, or when Claude fails, the data still commits and the next runs try the same changes again; after three failed attempts they are listed as not explained and the baseline moves on.
- `weekly-digest.yml` — runs `make install && make weekly` per track on Mondays 08:00 UTC.

To wire a new track in, add its directory name to `matrix.track` in `daily-update.yml` and `weekly-digest.yml`, add it to `TRACKS` and add an extractor for it in `scripts/insights/changes.py`, and add it to the `track` enum in `scripts/insights/schema.json`. The publish job reads its allowlist from `TRACKS`.

## Design Principles

- **Configuration-driven**: All sources, weights, and thresholds live in YAML configs.
- **Transparent scoring**: Every score is explainable; tune weights per track.
- **Historical traceability**: Normalized data, snapshots, and reports are committed for audit and trend analysis; raw API dumps stay local.
- **Template-first**: New tracks and deep dives start from proven scaffolds.
- **Automation-friendly**: Every step is scriptable and CI-ready.

## License

[MIT](LICENSE)
