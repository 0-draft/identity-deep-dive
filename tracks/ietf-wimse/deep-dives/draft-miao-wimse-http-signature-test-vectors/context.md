# Context

## Trigger

Revision -00 was posted on 18 November 2026 as an individual submission with intended status Informational; Datatracker lists no working group. It is the Internet-Draft form of v4 of a vector set first posted on 6 November 2026 in issue #419 of ietf-wg-wimse/draft-ietf-wimse-s2s-protocol and announced the same day on the WIMSE list as "Test vectors for draft-ietf-wimse-http-signature-08 — request for review" (Section 1, Appendix B).

The repository name in Section 1 is correct. ietf-wg-wimse/draft-ietf-wimse-s2s-protocol is the WIMSE working area that builds several drafts, among them draft-ietf-wimse-http-signature, draft-ietf-wimse-workload-creds, draft-ietf-wimse-wpt and draft-ietf-wimse-mutual-tls (repository README). The name comes from draft-ietf-wimse-s2s-protocol, from which draft-ietf-wimse-http-signature-00 was extracted (base -08 Appendix B.9).

Review happened on the issue and the list. On 7 November 2026 Yaron Sheffer, co-author of the base, asked for the `@query` lines to carry the leading `?`, answered on the list that "a MUST NOT in any security RFC should be rejected by the recipient", and opened issue #420 for the example-nonce note. Two independent runs were posted on the issue (7 and 11 November 2026), the P-04 `@authority` value was corrected on 13 November, and the issue was closed on 16 November 2026 ("Closing, nothing more to address in the draft."). draft-ietf-wimse-http-signature-09 followed on 20 November 2026; its change log cites #419 for the CONNECT `@authority` wording and #420 for the example-nonce note (-09 Appendix B.1).

## Why This Matters

The base draft is in AD Evaluation at the IESG (Datatracker, checked 26 November 2026), so its text is close to final. Its own examples cover two positive exchanges (base Sections 3.7.1, 3.7.2). This set adds 23 negatives, each tied to one MUST, plus published keys, so that implementations can compare decisions instead of only compare signatures. Writing the vectors already moved the base: two of its points are in -09. It also shows where the base states a rule only for senders (`keyid`, `alg`, coverage, CONNECT) and a verifier has to decide whether to enforce it. Some of the draft's own text needs checking before use: the placeholder in the signature bases is not what is signed, and the N-04 note says the signature fails when it does not.

## Open Questions

- Will the WIMSE working group take the set, and in what form? Yaron Sheffer suggested on issue #419 (7 November 2026) that the author ask the chairs.
- Will a -01 move the base reference to -09, drop O-2 (the note is now in -09 Section 3.7) and update the N-20 cross-reference to Section 5.1.3 of the workload credentials draft?
- Should the base say that recipients reject messages that break sender-only rules (N-01, N-02, N-06, N-07, N-21)? The 7 November list reply says so, but -09 has no such text.
- What exactly is the "deterministic expansion" of the WIT placeholder (Section 2), and where is the companion conformance suite that the v4 note on issue #419 mentions?
- Will the N-04 note be corrected, and will the cred-ninja run be repeated on all 29 vectors?
