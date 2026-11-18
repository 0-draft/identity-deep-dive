# Identity Deep Dive

Collect, score, and surface deep-dive candidates across OAuth WG, WIMSE, and OpenID Foundation specs.

**Site: <https://0-draft.github.io/identity-deep-dive/>** (English, [日本語](https://0-draft.github.io/identity-deep-dive/ja/)) · README: [日本語](README.ja.md)

This repo watches identity standards work, explains what changed with Claude, and keeps the results as data and a site:

- **Briefings**: every six hours, new draft revisions, mailing-list threads and PRs are explained with a summary, a diagram and use cases, plus weekly picks.
- **Spec map**: OAuth, OpenID and workload-identity specs by layer, with status, relations, explainers and adoption claims checked daily against their cited pages.
- **Deep dives**: per-topic investigations (context, spec notes, interop checklist, hands-on log), drafted weekly from the source text and reviewed before merge.

## Tracks

| Track                            | Scope                                          | Sources                           |
| -------------------------------- | ---------------------------------------------- | --------------------------------- |
| [IETF WIMSE](tracks/ietf-wimse/) | Workload Identity in Multi-System Environments | Datatracker, Mail Archive, GitHub |
| [OAuth WG](tracks/oauth-wg/)     | OAuth Working Group drafts and implementations | Datatracker, Mail Archive, GitHub |
| [OpenID](tracks/openid/)         | OpenID Foundation specifications and repos     | GitHub                            |

Each track runs the same pipeline:

```text
Collect  ->  Normalize  ->  Score  ->  Report  ->  Explain  ->  Synthesize
```

## Quick start

```bash
cd tracks/ietf-wimse
python3 -m venv .venv && source .venv/bin/activate
make install
make update        # collect + normalize + score + daily report
make weekly        # collect + normalize + score + weekly digest
```

To add a track, copy `templates/new-track` to `tracks/<name>` and wire it in as in [docs/automation.md](docs/automation.md#wiring-a-new-track). To start a deep dive, copy `templates/deep-dive` to `tracks/<track>/deep-dives/<topic>`.

## Layout

```text
tracks/              Per-track pipelines, reports and deep dives
data/                Spec map, explainers, RFC texts, synthesis
templates/           Scaffolds for tracks, deep dives, spec explainers, lab reports
scripts/             Shared code (insights, deep-dive drafts, spec map, RFC translation)
web/                 The site
.github/workflows/   CI
```

## Docs

- [docs/automation.md](docs/automation.md): pipeline steps, every workflow, and wiring a new track
- [docs/site.md](docs/site.md): the site's pages and where their data lives

## License

[MIT](LICENSE)
