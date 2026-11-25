# Context

## Trigger

openid/sharedsignals was the highest-ranked `openid` candidate without a deep dive in `tracks/openid/data/normalized/candidates.json` (snapshot 2026-11-24, rank 3, score 14.4). `tracks/openid/data/normalized/insights.json` recorded one new commit on `main`, "Drop event signatures (#368)" (`d8f89ab`, 17 November 2026).

## Why This Matters

The repository holds the SSF, CAEP and RISC 1.0 Final Specifications (approval announced 2 September 2025), the SSF 1.1 and CAEP 1.1 drafts created by #310 on 13 November 2026, and the draft CAEP Interoperability Profile. #368 changes only the profile: it deletes the rule that all events MUST be signed with `RS256` and 2048-bit keys. SSF itself never required signing or named an algorithm (SSF 1.0 Sections 4.1.4 and 7.1), so after #368 nothing in the repository fixes how SETs are signed. #355 proposes per-stream algorithm negotiation for SSF 1.1 and is still open.

## Open Questions

- Does the WG want the profile to require signed events at all? It still requires `jwks_uri` to serve signing keys (profile Sections 2.3.3 and 2.4.2).
- Will #355 land in SSF 1.1, and will the profile move to SSF 1.1?
- What compatibility policy will SSF 1.1 have once its text diverges from 1.0? At `d8f89ab` the two texts differ only in title and document name.
