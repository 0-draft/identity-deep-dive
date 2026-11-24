# Context

## Trigger

`subject.json` records no reason for the pick (`ai_note` is empty). The only earlier signal is a briefing in `insights.md` about one new commit on the default branch, "Drop event signatures (#368)".

## Why This Matters

The repository is where SSF, CAEP and RISC are developed, and it now holds SSF 1.1 and CAEP 1.1 drafts next to the retained 1.0 Final Specifications. Changes there can affect Transmitters and Receivers that implement 1.0. The material has only titles for the pull requests, so the size of each change is unknown.

## Open Questions

- What does #368 remove, and why?
- How do the open signing algorithm negotiation (#355) and the closed algorithm strictness change (#356) relate to it?
- Is 1.1 backward compatible with 1.0?
