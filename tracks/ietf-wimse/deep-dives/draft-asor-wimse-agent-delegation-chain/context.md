# Context

## Trigger

`subject.json` lists this as "Review related draft: draft-asor-wimse-agent-delegation-chain-03" on the ietf-wimse track. Its ai_note says the delegator-bound chains draft extends this draft's Delegation Tokens format and asks whether binding belongs in it; the repository's candidate data names that draft as draft-nandakumar-wimse-delegator-bound-chains-00 (2026-11-16). `subject.json` lists no Datatracker states, which fits an individual draft (draft-asor-, not draft-ietf-wimse-) that the working group has not adopted. The repository's WIMSE mail data covers 10 to 17 November 2026 and has no message on this draft; the only list dates in hand are the 23 and 24 October 2026 messages that Appendix A cites.

## Why This Matters

The draft targets one question in agent systems: when an agent hands work to another agent, how does the component that finally honors a tool call know that no hop exceeded the authority of the hop before it, without calling an authorization server? It answers with signed tokens linked by a parent hash, a subsumption relation over scopes and constraints, and an eight-step offline algorithm (Sections 4.3, 5, 6). Revision 03 matters because it states more of the limits: Principal standing is not established by the chain (Section 6.1, Table 1), root-key provenance is split into a binding gap and a recording gap (Section 6.4), and aggregate budgets need machinery outside the token (Section 9.4). It also leaves the registration of the three shared claim names to draft-niyikiza-oauth-attenuating-agent-tokens, a draft it says it intends to converge with (Section 1.1), while recording that the two define "del_max_depth" differently (Section 10).

## Open Questions

- Does binding a chain to a delegator belong in this token format, as the ai_note asks? The draft already carries "sub" and "client_id" at every hop (Section 3.1), but step 1 of Section 6 names no key that a child token must verify under. Only the abstract of the nandakumar draft was read.
- How will the "del_max_depth" difference with draft-niyikiza-oauth-attenuating-agent-tokens be resolved, so that each claim name has a single registration (Section 10)?
- Who defines scope vocabulary, trust-anchor provenance and Principal standing checks? The draft expects a companion document for the first (Section 4.5), puts the second to the working group in the author's view (Section 6.4), and leaves the third to the deployment (Section 6.1).
- How will multi-type authorization details work, given that -03 only records a proposed rule (Section 4.4)?
