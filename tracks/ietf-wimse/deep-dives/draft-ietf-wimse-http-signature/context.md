# Context

## Trigger

The subject was picked as an active working-group draft with a new revision to diff: draft-ietf-wimse-http-signature-08. The pick note says three new issues target this draft: test vectors (#419), nonce entropy in examples (#420) and editorial comments (#417). The datatracker states are Active, Publication Requested and Submitted to IESG for Publication.

## Why This Matters

The draft is close to the end of the working-group process, so the -08 changes are the last chance to settle behaviour before IESG review. -08 turns several loose points into MUSTs: nonce generation and entropy, the 400 and 501 error behaviour with registered problem types, TLS use, and Simple String Comparison for `wimse-aud`. It also adds a CONNECT exception. Independent test vectors written against -08 were posted to the WIMSE list, and a reviewer sent comments on the introduction. Implementers of -07 need to check what changed, and anyone writing a verifier now has shared inputs to test against.

## Open Questions

- Whether a verifier rejects or ignores `keyid` and `alg` when present: the draft only says senders MUST NOT use them (Section 3).
- What the default `wimse-aud` is for CONNECT, whose target is in authority-form (Sections 3, 3.2).
- How to tell "unsupported" from "unavailable" signing when the peer does not accept problem details (Section 3.6).
- What issue #420 on example nonces asks for: the staged material shows only the list thread that suggests an "illustrative" note.
- Whether the introduction text proposed in the review (issue #417) is adopted: -08 Section 1 does not contain it.
