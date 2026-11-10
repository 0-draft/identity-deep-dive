# Spec Notes

## References

Normative references listed in -08 (Section 8.1):

- BCP 195 (RFC 8996 and RFC 9325), new in -08.
- draft-ietf-wimse-workload-creds-02 (Workload Identity Token, WIT validation in its Section 5.1.4).
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
- draft-ietf-wimse-arch-08 (terminology and architecture). The -07 diff shows it in the normative list and the -08 text in the informative list, so the move is visible in the staged material, but the draft does not explain it.
- draft-ietf-wimse-mutual-tls-02.
- draft-ietf-wimse-wpt-02 (the DPoP-inspired alternative).
- The IANA HTTP Message Signature registry.
- RFC 9449 (DPoP).
- RFC 9864 (Ed25519 in the examples).

## Key Changes

- Section 3: CONNECT exception for requests and signed responses (`@method` and `@authority` instead of `@path` and `@query`).
- Section 3: Content-Digest cites RFC 9530. Nonce needs a cryptographically secure random number generator and at least 64 bits of entropy (96 or more RECOMMENDED). Recipients MUST reject signatures outside the validity window. A server-authenticated TLS connection and client hostname validation are required in this section.
- Section 3.1: algorithm baseline wording changed to "follow the algorithm requirements" of the workload credentials draft.
- Section 3.2: `wimse-aud` is compared with Simple String Comparison against the recipient's trusted configuration, and the audience must not be derived from Host.
- Section 3.3: `wimse-sign-response` set to true obliges the server to sign or return an error.
- Section 3.6: 400 with `wimse-signature-invalid` for any authentication failure, with no indication of which check failed. 501 with `wimse-signed-response-unsupported` and 400 with `wimse-signed-response-unavailable` when required signing fails. Problem details are SHOULD.
- Section 7.2: three HTTP Problem Types registrations.
- Restructuring: Security Goals are now Appendix A, Document History Appendix B, the DPoP comparison Appendix C. Section 6 Privacy Considerations is reduced to a pointer. Section 5 MUSTs were restated as descriptive text that refers to Section 3.
- Document history for -08 lists the shepherd review (#385), the CONNECT exception (#368) and Simple String Comparison (#396). The nonce, TLS, error-handling and IANA changes are not listed in that history, although they appear in the diff.
- Metadata: expiry moved to 23 April 2027 and the second author's affiliation changed from Intuit to Independent.

## Impact Analysis

- Upstream: depends on RFC 9421 for the signature mechanics, on the WIMSE workload credentials draft for the WIT and its validation, and on RFC 9457 and the HTTP Problem Types registry for error bodies. The new reference to RFC 9530 affects how Content-Digest is produced.
- Downstream: implementers of the Cofide and wimsey proof-of-concept code listed in Section 4, and test authors using the vector set discussed on the list, will need to follow the -08 rules. The draft does not state which revision either implementation tracks. IANA must register three signature metadata parameters and three problem types.
- Compatibility: -08 is not shown to change the wire format of a correct -07 message, except for CONNECT, but it tightens what verifiers may accept (nonce entropy, exact audience match, time window) and what servers must return (400 or 501 with problem types). Senders that relied on normalized audience comparison, short nonces or other error codes can fail. The draft does not discuss a transition period.
