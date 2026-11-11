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
