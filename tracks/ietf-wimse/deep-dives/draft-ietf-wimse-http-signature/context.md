# Context

## Trigger

The subject was picked as an active working-group draft with a new revision to diff: draft-ietf-wimse-http-signature-08. The pick note says three new issues target this draft: test vectors (#419), nonce entropy in examples (#420) and editorial comments (#417). The datatracker states are Active, Publication Requested and Submitted to IESG for Publication.

## Why This Matters

The draft is close to the end of the working-group process, so the -08 changes are the last chance to settle behaviour before IESG review. -08 turns several loose points into MUSTs: nonce generation and entropy, the 400 and 501 error behaviour, and Simple String Comparison for `wimse-aud`. It registers three problem types, moves the existing TLS MUST from Security Considerations into Section 3, and adds a CONNECT exception. Independent test vectors written against -08 were posted in issue #419 and announced on the WIMSE list, and a reviewer sent comments on the introduction. Implementers of -07 need to check what changed, and anyone writing a verifier now has shared inputs to test against.

## Open Questions

- Whether a verifier rejects or ignores `keyid` and `alg` when present: the draft only says senders MUST NOT use them (Section 3). Yaron Sheffer's reply on the list (7 November 2026) favours rejecting, but the text does not say so.
- What the default `wimse-aud` is for CONNECT, whose target is in authority-form (Sections 3, 3.2).
- How to tell "unsupported" from "unavailable" signing when the peer does not accept problem details (Section 3.6).
- When issue #420 lands: it asks for an editorial note that the Section 3.7 example nonces (such as `abcd1111`) are illustrative and below the 64-bit minimum. It is open.
- Whether the introduction text proposed in Kathleen Moriarty's review (issue #417) is adopted: the issue is open with no decision, and -08 Section 1 does not contain it.
