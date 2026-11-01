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
Collect  ->  Normalize  ->  Score  ->  Report  ->  Explain  ->  Synthesize
  raw API       JSON         ranked      daily/weekly   Claude       picks +
  snapshots     merge        backlog     markdown       briefing     topic map
```

1. **Collect** — Fetch raw data from configured sources (GitHub API, IETF Datatracker, mailing lists).
2. **Normalize** — Transform raw data into a consistent JSON schema per track.
3. **Score** — Rank items by lifecycle state, recency, and activity to surface what matters now.
4. **Report** — Generate daily and weekly markdown reports with prioritized tables.
5. **Explain** — In CI, find what is new since the last explained state (draft revisions, new drafts, mailing-list threads, PRs, repository activity), fetch the source material, and have Claude explain each item: a one-line headline, a summary grounded in the diff or message, a mermaid diagram of the mechanism, use cases, and links to related items in the other tracks. Claude also flags deep-dive candidates to move up or down: `candidates.json` and the site list raised candidates first, and a "Triage" section is appended to `deep-dives/_backlog.md`. The result lands in a "Briefing" section at the top of the daily report and in `data/normalized/insights.json` (a rolling seven-day window). See `scripts/insights/`.
6. **Synthesize** — After each publish, a synthesis pass reads every track's recent explanations and draft lists and writes `data/synthesis.json`: three to five picks for the week with why each matters, and a topic map grouping drafts and repositories. Explanations and synthesis carry Japanese twins of every text field.

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

Three of the workflows in `.github/workflows/` run the tracks, and one refreshes the spec map (the others build the site, run PR checks and review pull requests):

- `daily-update.yml` — every six hours. A read-only `collect` job per track runs `make install && make update`, stages what is new since the last explained state (`data/normalized/insights_baseline.json`), and has Claude explain it with read-only tools and structured output. A separate `publish` job, with no model in it, validates the result with `scripts/insights/apply.py`, commits per track and pushes. Without the `CLAUDE_CODE_OAUTH_TOKEN` secret, or when Claude fails, the data still commits and the next runs try the same changes again; after three failed attempts they are listed as not explained and the baseline moves on.
- `weekly-digest.yml` — runs `make install && make weekly` per track on Mondays 08:00 UTC.
- `deep-dive-draft.yml` — on Tuesdays (or on demand for one track or candidate), takes each track's highest-ranked candidate (after triage) that is a draft or an OpenID repository and has no deep dive, open branch or earlier pull request, has Claude draft `README.md`, `context.md`, `spec-notes.md` and `interop-checklist.md` from the staged source text (the draft, capped at 250,000 characters, with its latest revision diff and mailing-list messages; for an OpenID repository, its README and recent pull request titles), and opens a draft pull request listing the statements a reviewer should check. See `scripts/deep_dive/`.
- `landscape.yml` — on Wednesdays, with no model, runs `scripts/landscape/refresh.py`: reads each IETF spec's state from the Datatracker, checks that every OpenID status and adoption claim's evidence phrase is still on its cited page, and commits `data/landscape-status.json`; the run fails if any status or claim was not verified (after committing, so failed claims show as not re-verified). The `landscape-evidence` PR check runs the same verification with `--check` and fails if any status or claim is not found; its uploaded `landscape-status` artifact is the status file to commit with a change to the sources.

To wire a new track in: add it to `TRACKS` in `scripts/insights/tracks.py` (the deep-dive matrix and the publish allowlist read it from there), to `matrix.track` in `daily-update.yml` and `weekly-digest.yml`, to the `track` choice of `deep-dive-draft.yml`, and to the `track` enum in `scripts/insights/schema.json`; then add an extractor for it in `scripts/insights/changes.py`.

## Site

`web/` builds the GitHub Pages site, in English at `/` and in Japanese at `/ja/`. Model-written text uses its Japanese twin and falls back to English when there is none. On Japanese pages, the report headings, labels and fixed sentences are translated; the data in them stays as written.

- The home page leads with the week's picks, then a board of every IETF draft by Datatracker state (individual, working group, WG last call, IESG, RFC Editor), the topic map, and the rest of the recent explanations.
- Each track page has its briefing, its board, every explanation with its diagram and use cases, its deep dives, the deep-dive queue with triage, and the full reports.
- The spec map at `/map/` places OAuth, OpenID, workload-identity and credential specs by layer, with each one's status, what it builds on or replaces, and who documents support for it. The specs, relations and summaries are curated in `data/landscape.json`; OpenID statuses and adoption claims in `data/landscape-sources.json`, each with an official URL and a phrase quoted from that page. Only claims whose phrase was found at the last weekly check are listed as adoption.
- Each deep dive has its own page at `/<track>/deep-dives/<slug>/`, with diagrams rendered. A file's Japanese edition is `<name>.ja.md` next to it. The weekly deep-dive job asks for one with every drafted file (the empty hands-on log comes from a Japanese template), and its PR lists which were written and any whose headings, list items, code fences or backticked identifiers differ from the English. Missing ones fall back to English on the site, marked as such.

## Design Principles

- **Configuration-driven**: All sources, weights, and thresholds live in YAML configs.
- **Transparent scoring**: Every score is explainable; tune weights per track.
- **Historical traceability**: Normalized data, snapshots, and reports are committed for audit and trend analysis; raw API dumps stay local.
- **Template-first**: New tracks and deep dives start from proven scaffolds.
- **Automation-friendly**: Every step is scriptable and CI-ready.

## License

[MIT](LICENSE)
