# Site

`web/` builds the [GitHub Pages site](https://0-draft.github.io/identity-deep-dive/), in English at `/` and in Japanese at `/ja/`. Model-written text uses its Japanese twin and falls back to English when there is none. On Japanese pages, the report headings, labels and fixed sentences are translated; the data in them stays as written.

## Pages

- **Home**: the week's picks, then a board of every IETF draft by Datatracker state (individual, working group, WG last call, IESG, RFC Editor), the topic map, and the rest of the recent explanations.
- **Track pages**: the track's briefing, its board, every explanation with its diagram and use cases, its deep dives, the deep-dive queue with triage, and the full reports.
- **Spec map** (`/map/`): OAuth, OpenID, workload-identity and credential specs by layer, with each one's status, what it builds on or replaces, and who documents support for it. It opens with the specs that moved in the last 90 days (new revisions, explanations on the site, mailing-list threads naming the draft) and ends with the working-group drafts the tracks follow that are not on the map yet.
- **Spec pages** (`/map/<id>/`): an explainer with when to reach for it, the problem, how it works with diagrams, what the spec requires, pitfalls and sources, all cited to the official text; the relations graph; documented support split into products and open-source implementations; and the spec's activity (revision timeline, explanations, mailing-list subjects).
- **RFC pages** (`/map/<id>/rfc/`): the English text from the RFC Editor on the left, a Japanese machine translation on the right, aligned paragraph by paragraph. Examples, figures and references stay English; only the English is authoritative.
- **Deep dives** (`/<track>/deep-dives/<slug>/`): each deep dive with diagrams rendered.

## Where the data lives

| Content                          | Source                                                                                                                                                                                       |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Specs, relations, summaries      | `data/landscape.json` (curated)                                                                                                                                                              |
| OpenID statuses, adoption claims | `data/landscape-sources.json`, each with an official URL and a phrase quoted from that page. Only claims whose phrase was found at the last daily check are listed as adoption.              |
| Spec explainers                  | `data/specs/<id>/README.md`, Japanese edition `README.ja.md`, template in `templates/spec-explainer/`. Written from the official text and reviewed statement by statement before they merge. |
| RFC text and translation         | `data/rfc/<n>/`                                                                                                                                                                              |
| Deep dives                       | `tracks/<track>/deep-dives/<slug>/`                                                                                                                                                          |

## Japanese editions of deep dives

A file's Japanese edition is `<name>.ja.md` next to it. The weekly deep-dive job asks for one with every drafted file (the empty hands-on log comes from a Japanese template), and its PR lists which were written and any whose headings, list items, code fences or backticked identifiers differ from the English. Missing ones fall back to English on the site, marked as such.
