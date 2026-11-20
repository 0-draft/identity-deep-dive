# CLAUDE.md

Guidance for Claude Code working in this repo. The overview is in [README.md](README.md); the pipeline and every workflow are in [docs/automation.md](docs/automation.md); the site's pages and where their data lives are in [docs/site.md](docs/site.md). Read those instead of re-deriving the layout.

## Checks

Run what `pr-checks.yml` runs before calling a change done. Check each exit code directly; never gate a commit on `check | tail`, the pipe hides the failure.

```bash
(cd web && npm ci && npm run check && npm run build)
python3 -m compileall -q tracks/*/scripts scripts
python3 scripts/landscape/explainers.py          # spec explainers match their template
python3 scripts/landscape/refresh.py --check     # every status / adoption claim is still on its cited page
shellcheck scripts/*.sh tracks/*/scripts/*.sh
npx --yes markdownlint-cli2 --config ~/.markdownlint-cli2.jsonc "**/*.md" "#web/node_modules"
```

A track's pipeline runs locally with `cd tracks/<track> && make install && make update` (or `make weekly`).

## Rules

- **A push to `main` deploys Pages.** Commit per logical change and push each one as it lands, but only after `npm run build` passes.
- **English and Japanese stay in step.** A change to an explainer, a deep dive or the README changes its `.ja.md` twin in the same commit: same headings, list items, code fences and backticked identifiers.
- **Every spec-map claim is evidenced.** A new status or adoption claim in `data/landscape-sources.json` needs an official URL and a phrase quoted from that page, and must pass `refresh.py --check`. Explainers are written from the official text and checked statement by statement against it.
- **Model-drafted PRs are reviewed, not trusted.** The weekly deep-dive drafts and RFC translations open as draft PRs; check each listed statement against the primary source before merge.
- **Finish the review loop before merging.** After each push, wait for the Claude review run, list every inline thread with `gh api --paginate repos/0-draft/identity-deep-dive/pulls/<n>/comments` (the default page is 30), and reply to each with the fixing commit or the evidence it is not a bug.
- **Comments to upstream WGs are terse.** One line per point, section numbers instead of quoted spec text, no explaining why it matters.

The periodic upkeep (job health, deep-dive PR review, spec-map refresh, visual check) is the `refresh-identity-deep-dive` skill.
