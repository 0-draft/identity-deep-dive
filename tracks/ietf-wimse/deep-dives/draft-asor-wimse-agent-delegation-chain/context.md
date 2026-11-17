# Context

## Trigger

`subject.json` lists this as "Review related draft: draft-asor-wimse-agent-delegation-chain-03" on the ietf-wimse track. Its ai_note says the delegator-bound chains draft extends this draft's Delegation Tokens format and asks whether binding belongs in it. `subject.json` lists no Datatracker states, and no mailing-list material was staged.

## Why This Matters

The draft targets one question in agent systems: when an agent hands work to another agent, how does the component that finally honors a tool call know that no hop exceeded the authority of the hop before it, without calling an authorization server? It answers with signed tokens linked by a parent hash, a subsumption relation over scopes and constraints, and an eight-step offline algorithm (Sections 4.3, 5, 6). Revision 03 matters because it states more of the limits: Principal standing is not established by the chain (Section 6.1, Table 1), root-key provenance is split into a binding gap and a recording gap (Section 6.4), and aggregate budgets need machinery outside the token (Section 9.4). It also yields to a competing draft on claim registrations while noting a real semantic difference in "del_max_depth" (Section 10).

## Open Questions

- Does binding a chain to a delegator belong in this token format, as the ai_note asks? The draft already carries "sub" and "client_id" at every hop (Section 3.1), and the staged material does not show the other draft.
- How will the "del_max_depth" difference with draft-niyikiza-oauth-attenuating-agent-tokens be resolved, so that each claim name has a single registration (Section 10)?
- Who defines scope vocabulary, trust-anchor provenance and Principal standing checks? The draft leaves each to the working group or the deployment (Sections 4.5, 6.4, 6.1).
- How will multi-type authorization details work, given that -03 only records a proposed rule (Section 4.4)?
