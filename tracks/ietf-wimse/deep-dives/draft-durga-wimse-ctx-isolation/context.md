# Context

## Trigger

The draft was newly announced to the WIMSE mailing list with a request for review and a possible lightning slot at IETF 127 (`subject.json`, `mail.txt`). The announcement also covers a companion draft, draft-durga-agenttrust-trace-verification-00. No Datatracker states are recorded for this draft.

## Why This Matters

The draft addresses a gap that WIMSE token work does not cover: a workload can be correctly authenticated while the tool call it makes was shaped by untrusted content in an LLM context window (Section 1). It proposes to make that visible and enforceable at the relying party with a signed taint attestation. The idea is easy to state, but the evidence in revision 00 is thin: the signer is the agent runtime, the key is not tied to a workload identity, and the step-up receipt is not defined. A reviewer should treat it as an early problem statement with a sketch of a wire format.

## Open Questions

- Does the WG consider taint reporting in scope, and where would it sit relative to the Workload Identity Token and Workload Proof Token (Section 1)?
- How can a relying party trust a self-asserted taint level (Sections 3, 4)?
- Which fields mentioned in the announcement (`ctx_isolation_witness`, `policy_manifest_sha256`) will appear in a later revision? They are not in revision 00.
- How is the COSE_Sign1 statement in the Abstract reconciled with the plain JSON signature object in Section 3?
- Who owns the work: the header names both WIMSE and OAuth, and the intended status is Standards Track.
