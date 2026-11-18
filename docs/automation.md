# Automation

How the pipeline runs in CI. For the overview, see the [README](../README.md).

## Pipeline steps

Each track runs the same steps:

1. **Collect**: fetch raw data from configured sources (GitHub API, IETF Datatracker, mailing lists).
2. **Normalize**: transform raw data into a consistent JSON schema per track.
3. **Score**: rank items by lifecycle state, recency, and activity to surface what matters now.
4. **Report**: generate daily and weekly markdown reports with prioritized tables.
5. **Explain**: in CI, find what is new since the last explained state (draft revisions, new drafts, mailing-list threads, PRs, repository activity), fetch the source material, and have Claude explain each item: a one-line headline, a summary grounded in the diff or message, a mermaid diagram of the mechanism, use cases, and links to related items in the other tracks. Claude also flags deep-dive candidates to move up or down: `candidates.json` and the site list raised candidates first, and a "Triage" section is appended to `deep-dives/_backlog.md`. The result lands in a "Briefing" section at the top of the daily report and in `data/normalized/insights.json` (a rolling seven-day window). See `scripts/insights/`.
6. **Synthesize**: after each publish, a synthesis pass reads every track's recent explanations and draft lists and writes `data/synthesis.json`: three to five picks for the week with why each matters, and a topic map grouping drafts and repositories. Explanations and synthesis carry Japanese twins of every text field.

## Workflows

Three of the workflows in `.github/workflows/` run the tracks, and one refreshes the spec map (the others build the site, run PR checks and review pull requests):

- `daily-update.yml`: every six hours. A read-only `collect` job per track runs `make install && make update`, stages what is new since the last explained state (`data/normalized/insights_baseline.json`), and has Claude explain it with read-only tools and structured output. A separate `publish` job, with no model in it, validates the result with `scripts/insights/apply.py`, commits per track and pushes. Without the `CLAUDE_CODE_OAUTH_TOKEN` secret, or when Claude fails, the data still commits and the next runs try the same changes again; after three failed attempts they are listed as not explained and the baseline moves on.
- `weekly-digest.yml`: runs `make install && make weekly` per track on Mondays 08:00 UTC.
- `deep-dive-draft.yml`: on Tuesdays (or on demand for one track or candidate), takes each track's highest-ranked candidate (after triage) that is a draft or an OpenID repository and has no deep dive, open branch or earlier pull request, has Claude draft `README.md`, `context.md`, `spec-notes.md` and `interop-checklist.md` from the staged source text (the draft, capped at 250,000 characters, with its latest revision diff and mailing-list messages; for an OpenID repository, its README and recent pull request titles), and opens a draft pull request listing the statements a reviewer should check. See `scripts/deep_dive/`.
- `landscape.yml`: daily, with no model, runs `scripts/landscape/refresh.py`: reads each IETF spec's state and revision history from the Datatracker, checks that every OpenID status and adoption claim's evidence phrase is still on its cited page, and commits `data/landscape-status.json`; the run fails if any status or claim was not verified (after committing, so failed claims show as not re-verified). The `landscape-evidence` PR check (`landscape-check.yml`, on PRs that touch the map's data or script) runs the same verification with `--check` and fails if any status or claim is not found; its uploaded `landscape-status` artifact is the status file to commit with a change to the sources. The job summary also lists working-group drafts the tracks follow that have no entry on the map.
- `rfc-translate.yml`: on demand, for one RFC number: fetches the RFC's text (`scripts/rfc/fetch.py` cuts it into sections and paragraphs with stable ids, `data/rfc/<n>/en.json`), has Claude translate it chunk by chunk with read-only tools and structured output, imports the blocks (`scripts/rfc/import_ja.py`, `data/rfc/<n>/ja.json`) and opens a draft pull request. Paragraphs already translated are skipped, so a re-run fills gaps. See `scripts/rfc/`.

## Wiring a new track

After scaffolding the track (see the README), add it to:

1. `TRACKS` in `scripts/insights/tracks.py` (the deep-dive matrix and the publish allowlist read it from there).
2. `matrix.track` in `daily-update.yml` and `weekly-digest.yml`.
3. The `track` choice of `deep-dive-draft.yml`.
4. The `track` enum in `scripts/insights/schema.json`.
5. An extractor for it in `scripts/insights/changes.py`.
