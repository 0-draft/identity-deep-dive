# Spec Notes

## References

Normative references listed in -08 (Section 8.1):

- BCP 195 (RFC 8996 and RFC 9325), new in -08.
- draft-ietf-wimse-workload-creds-02 (Workload Identity Token). Sections 3 and 3.6 cite its "Section 5.1.4" for WIT validation, but -02 has no Section 5.1.4 (its Section 5.1.3 is the note on `iss` and key distribution). The validation procedure is Section 5.1.3 ("Validating the WIT") of workload-creds-03, posted on 30 October 2026, after -08.
- RFC 2119 and RFC 8174 (key words).
- RFC 3986 (Simple String Comparison, Section 6.2.1), new in -08.
- RFC 7942 (Implementation Status section).
- RFC 9110 (HTTP Semantics, including CONNECT in Section 9.3.6 and the target URI in Section 7.1).
- RFC 9421 (HTTP Message Signatures).
- RFC 9457 (Problem Details for HTTP APIs).
- RFC 9525 (hostname validation, Section 6.3).
- RFC 9530 (Digest Fields), new in -08.

Informative references (Section 8.2):

- draft-ietf-oauth-transaction-tokens-11 (Txn-Token header).
- draft-ietf-wimse-arch-08 (terminology and architecture). It was normative in -07 and is informative in -08: the draft source changes `{{!I-D.ietf-wimse-arch}}` to `{{?I-D.ietf-wimse-arch}}`. The reason is in the shepherd review (issue #385): "Is `wimse-arch` really normative? Expect informative; if normative, it is a downref."
- draft-ietf-wimse-mutual-tls-02.
- draft-ietf-wimse-wpt-02 (the DPoP-inspired alternative).
- The IANA HTTP Message Signature registry.
- RFC 9449 (DPoP).
- RFC 9864 (the fully-specified `Ed25519` identifier used in the examples).

The algorithm itself comes from `cnf.jwk.alg` in the WIT (Section 3.1). -08 sets no baseline of its own and defers to the workload credentials draft, where `ES256` MUST be supported by general-purpose implementations and any IANA JOSE signature algorithm other than `none`, symmetric or encryption algorithms is allowed. `Ed25519` is used in the examples but is not mandatory, and the deprecated `EdDSA` identifier is not excluded by either draft.

## Key Changes

- Section 3: CONNECT exception for requests and signed responses (`@method` and `@authority` instead of `@path` and `@query`).
- Section 3: Content-Digest cites RFC 9530. Nonce needs a cryptographically secure random number generator and at least 64 bits of entropy (96 or more RECOMMENDED). Recipients MUST reject signatures outside the validity window. A server-authenticated TLS connection and client hostname validation are required in this section.
- Section 3.1: algorithm baseline wording changed to "follow the algorithm requirements" of the workload credentials draft.
- Section 3.2: `wimse-aud` is compared with Simple String Comparison against the recipient's trusted configuration, and the audience must not be derived from Host.
- Section 3.3: `wimse-sign-response` set to true obliges the server to sign or return an error.
- Section 3.6: 400 with `wimse-signature-invalid` for any authentication failure, with no indication of which check failed. 501 with `wimse-signed-response-unsupported` and 400 with `wimse-signed-response-unavailable` when required signing fails. Problem details are SHOULD.
- Section 7.2: three HTTP Problem Types registrations.
- Restructuring: Security Goals move from Section 6 to Appendix A, so Document History becomes Appendix B and the DPoP comparison Appendix C. Privacy Considerations, Section 5.3 in -07, becomes Section 6 and is reduced to a pointer. Section 5 MUSTs were restated as descriptive text that refers to Section 3.
- Document history for -08 has three entries: the shepherd review (#385), the CONNECT exception (#368) and Simple String Comparison (#396). The nonce, TLS, error-handling, problem-type, Privacy, appendix and `wimse-arch` changes are not itemised there, but each matches a point in Justin Richer's shepherd notes in issue #385, which was closed on 20 October 2026 with every item ticked.
- Metadata: expiry moved to 23 April 2027 and the second author's affiliation changed from Intuit to Independent.

## Impact Analysis

- Upstream: depends on RFC 9421 for the signature mechanics, on the WIMSE workload credentials draft for the WIT and its validation, and on RFC 9457 and the HTTP Problem Types registry for error bodies. The new reference to RFC 9530 affects how Content-Digest is produced.
- Downstream: the Cofide (proof-of-concept) and wimsey (alpha) implementations listed in Section 4, and test authors using the issue #419 vector set, need to follow the -08 rules. Section 4 gives only last-updated dates (13 November 2025 and 8 September 2026). The Cofide repository says it implements draft-ietf-wimse-s2s-protocol and was last pushed on 14 November 2025, before -08. After -08 the main branch updates the wimsey entry to "signed responses as per version -08 of the draft" (PR #406, merged 23 October 2026). IANA must register three signature metadata parameters and three problem types.
- Compatibility: -08 is not shown to change the wire format of a correct -07 message, except for CONNECT, but it tightens what senders must produce (CSPRNG nonces with at least 64 bits of entropy), how verifiers compare `wimse-aud` (exact string match) and what servers must return (400 or 501 with problem types). Rejecting signatures outside the validity window was already a MUST in -07 (then in Section 5.1). Senders that relied on normalized audience comparison, short nonces or other error codes can fail. The draft does not discuss a transition period.

## Test Vector Re-run

On 11 November 2026 this repository ran the 28 vectors in issue #419 through a verifier written from the -08 text and RFC 9421, using the regenerated P-01, P-02, P-06 and N-15 values from the 7 November comment. The issue gives literal bytes only for the positive vectors and N-15. For the other negative vectors it describes a change to a positive vector, so the script builds those inputs itself, and they are this repository's reconstructions, not the issue's bytes. The script is [`vectors/verify_419.py`](https://github.com/0-draft/identity-deep-dive/blob/main/tracks/ietf-wimse/deep-dives/draft-ietf-wimse-http-signature/vectors/verify_419.py) and its output is [`vectors/verify_419.log`](https://github.com/0-draft/identity-deep-dive/blob/main/tracks/ietf-wimse/deep-dives/draft-ietf-wimse-http-signature/vectors/verify_419.log). The steps to reproduce it are in the hands-on log. As a check on the verifier itself, it rebuilds the signature base and re-signs with the published test keys, and all 8 published signatures come out byte for byte the same (log section 1).

- Inputs: P-01 to P-06 and N-15 are the published messages, and the script reproduces their 8 signatures byte for byte. N-04 (body swapped) and N-09 (later verification time) use a published message with its original signature, and N-14 is the published P-02 response with its signature removed. N-01, N-02, N-03, N-05, N-06, N-07, N-08, N-10, N-11, N-12 and N-13 apply the change and re-sign with the published test keys. N-21 is built from the issue's prose, which gives no values, and is signed the same way. N-16 to N-22 describe behaviour and are run as checks on the script's own sender, server and verifier logic.
- Result: all 22 accept/reject vectors (P-01 to P-06, N-01 to N-15, N-21) got the expected decision from this verifier. N-16, N-18, N-19 and N-22 describe sender, server or verifier behaviour. The script runs them against its own nonce generator, response checker and signature selection, so a match there only shows that the expected outcomes agree with the -08 text as the script reads it. It says nothing about another implementation. N-17 (the error must not reveal which check failed) and N-20 (verify the WIT before doing anything else) cannot be judged from a single message and were not scored.
- N-04: the issue says the changed body "also makes the signature fail". In the run it does not: only the body changes, `Content-Digest` keeps its original value, and that header is what the signature covers. The only failure the verifier reports is the digest recomputed from the received body (Section 3: "the receiver MUST compute the `Content-Digest` value for the message content received and compare it with the `Content-Digest` value provided in the message").
- N-09: verification time T0+3600 equals WIT-A's `exp`, so the WIT expiry and the signature validity window fail at the same instant. The script repeats the check at T0+301, where only the window check fails and the message is still rejected.
- N-15: the ES256 signature fails as an invalid signature under the Ed25519 key in `cnf.jwk`, and verifies under the svcC ES256 key. In a verifier that takes the key from `cnf.jwk`, the vector therefore never reaches the Section 3.1 "algorithm not allowed by local policy" check.
- Expected outcomes the -08 text states only as sender rules: N-06 and N-07 (`keyid` and `alg` "MUST NOT be used"), N-01 (required components "MUST be signed"), and N-02 and N-21 (CONNECT senders "MUST NOT cover `@path` or `@query`"). In this verifier, switching off receive-side enforcement of those rules makes all five of these accept (N-01, N-02, N-06, N-07 and N-21), since their signatures are valid. Whether another verifier rejects them depends on how it reads these sender rules.
- P-04 signs `@authority` as `svcb.example.com:443`. -08 Section 3 says "The `@authority` value is the host and port of the CONNECT target (Section 2.2.3 of RFC9421)". RFC 9421 Section 2.2.3 says "The component value MUST be normalized according to the rules provided in [HTTP], Section 4.2.3. Namely, the hostname is normalized to lowercase, and the default port is omitted." A CONNECT target in authority form has no scheme, and neither text says whether 443 counts as its default port, so implementations can disagree on this value.
