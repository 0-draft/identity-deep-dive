# Context

## Trigger

`subject.json` gives no reason for the pick (`ai_note` is empty). The earlier briefing in `insights.md` reported that PR #800 (branch 718-age-over-nn) was merged, but it had no diff, so the effect was unknown. That briefing is a pointer only. The README independently lists #800 "Add support for age_over_nn claims matching" as closed and merged.

## Why This Matters

The repository holds the 1.0 and 1.1 working-group drafts of OpenID for Verifiable Presentations. The README lists about thirty recently updated pull requests, mostly merged clarifications on error handling, matching of `vct` and `doctype`, client metadata, security guidance and the DC API. Implementers of wallets and verifiers depend on these details to interoperate. The staged material does not include the specification text or any diff, so the actual wording changes are not verified here.

## Open Questions

- What does #800 change about age_over_nn claims matching?
- Which merged changes apply to 1.0 and which to 1.1?
- What is the status of #726, #808 and #804, which are still open?
- Why was #647 closed without a merge?
