# CLAUDE.md

Guidance for Claude Code working in this repo. The overview is in [README.md](README.md); the pipeline and every workflow are in [docs/automation.md](docs/automation.md); the site's pages and where their data lives are in [docs/site.md](docs/site.md). Read those instead of re-deriving the layout.

## Checks

Before calling a change done, run the checks in `.github/workflows/pr-checks.yml` that touch what you changed. Check each exit code directly; never gate a commit on `check | tail`, the pipe hides the failure.

```bash
(cd web && npm ci && npm run check && npm run build)
python3 -m compileall -q tracks/*/scripts scripts
python3 scripts/landscape/explainers.py          # spec explainers match their template
shellcheck scripts/*.sh tracks/*/scripts/*.sh
```

`pr-checks.yml` also checks that `data/rfc/*/ja.json` only translates paragraphs that exist in `en.json`. That script is inline in the workflow; copy it from there when you touch `data/rfc/`.

`scripts/landscape/refresh.py --check` (every status and adoption claim still on its cited page) runs in `landscape-check.yml` on PRs that touch `data/landscape*.json` or `scripts/landscape/`. Leave it to that check: locally it needs `requests` and reaches dozens of vendor sites that the sandbox allowlist does not cover.

Markdown is not linted in CI. Lint only the files you changed with `npx --yes markdownlint-cli2 --config ~/.markdownlint-cli2.jsonc <files>`: about ten existing files do not pass (the generated `tracks/*/reports/`, the templates, and one deep dive), so a whole-repo run always fails.

A track's pipeline runs locally inside a venv (Homebrew's Python refuses `pip install`): `cd tracks/<track> && python3 -m venv .venv && . .venv/bin/activate && make install && make update` (or `make weekly`). Collection reads `mailarchive.ietf.org`, which the sandbox does not allow, so a full run belongs in CI or outside the sandbox.

## Rules

- **A push to `main` deploys Pages.** Commit per logical change and push each one as it lands, but only after `npm run build` passes.
- **English and Japanese stay in step.** A change to an explainer, a deep dive or the README changes its `.ja.md` twin in the same commit: same headings, list items, code fences and backticked identifiers.
- **Every spec-map claim is evidenced.** A new status or adoption claim in `data/landscape-sources.json` needs an official URL and a phrase quoted from that page, and must pass `refresh.py --check`. Explainers are written from the official text and checked statement by statement against it.
- **Model-drafted PRs are reviewed, not trusted.** The weekly deep-dive drafts and RFC translations open as draft PRs; check each listed statement against the primary source before merge.
- **Finish the review loop before merging.** The Claude review (`claude-review.yml`) skips draft PRs, and the deep-dive and RFC PRs open as drafts, so mark one ready for review before expecting it. After each push, wait for the review run, list every inline thread with `gh api --paginate repos/0-draft/identity-deep-dive/pulls/<n>/comments` (the default page is 30), and reply to each with the fixing commit or the evidence it is not a bug.
- **Comments to upstream WGs are terse.** One line per point, section numbers instead of quoted spec text, no explaining why it matters.

The periodic upkeep (job health, deep-dive PR review, spec-map refresh, visual check) is the `refresh-identity-deep-dive` skill.
