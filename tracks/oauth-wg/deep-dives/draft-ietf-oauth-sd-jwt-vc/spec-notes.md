# Spec Notes

## References

Normative references listed in the draft (Section 10.1 of -26):

- [I-D.ietf-oauth-status-list] draft-ietf-oauth-status-list-21.
- RFC 2119, RFC 8174 (BCP 14), RFC 2397 (data URL scheme), RFC 3986 (URI syntax), RFC 5280 (X.509 PKI profile, normative since -24), RFC 5646 (language tags).
- RFC 7515 (JWS), RFC 7517 (JWK), RFC 7519 (JWT), RFC 7800 (proof-of-possession key semantics), RFC 8615 (well-known URIs).
- RFC 9110 (HTTP Semantics), RFC 9111 (HTTP Caching), RFC 9901 (SD-JWT).
- [W3C.CSS-COLOR] CSS Color Module Level 3, [W3C.SRI] Subresource Integrity, [W3C.SVG] SVG 1.1 Second Edition (since -24).

RFC 6890 was a normative reference up to -25. -26 removed it.

Informative references (Section 10.2 of -26):

- [EUDIW.ARF], [IANA.IPv4-Special-Registry], [IANA.IPv6-Special-Registry] (both since -26), [IANA.JWT], [IANA.MediaTypes], [IANA.well-known], [NIST-BLOG.VDCE], [OWASP_SSRF].
- RFC 6901 (JSON Pointer), RFC 9205 (Building Protocols with HTTP), RFC 9535 (JSONPath), [UAX9] (Unicode Bidirectional Algorithm).

## Key Changes

Changes in -24 (5 November 2026) relative to -23, answering the IESG ballot:

- Header `Updates: 7800 (if approved)` and a sentence in the abstract.
- New Section 2.2.2.3.1 "Confirmation Claim Independence": the draft "explicitly overrides that requirement and updates [RFC7800] to nullify that requirement", for "key-bound SD-JWT VCs, SD-JWTs, and JWTs".
- Section 2.5: `x5c` chain validated "according to Section 4.1.6 of [RFC7515] and [RFC5280]"; a certificate in `x5c` "is not a trust anchor merely because it is included there"; under `x5c` an `iss` is not authenticated, a recipient MAY reject an `iss` not bound to the certificate, and Issuers SHOULD NOT include an `iss` without such a binding; "The recipient's policy determines which mechanism applies to an Issuer; the SD-JWT VC does not"; a recipient MUST NOT treat inputs of another mechanism as identifying the Issuer unless policy binds them and the binding is verified.
- Section 7.3: the Issuer is the one identified by the mechanism in use, the MUST is "for any given Issuer", and a mechanism "authenticates only its own inputs".
- Section 4: lowercasing the scheme and host of `iss` is RECOMMENDED.
- Keyword fixes in Sections 2.2, 2.2.2.5, 5.3.3, 5.5.1.2.1 and 7.6. New normative references RFC 5280 and [W3C.SVG]. The encoded examples carry `typ` `vc+sd-jwt` (Figure 2 says `dc+sd-jwt`), a KB-JWT `iat` of 1724705969 and other Appendix A.1 data (Erika Mustermann).

Changes in -25 (5 November 2026):

- Section 2.2.2.2: "SHOULD treat an SD-JWT VC as being of a given type" becomes "treats".
- Section 2.4: the status check stays SHOULD; new sentence that a Verifier that does not check status cannot detect revocation or suspension "and accepts that risk according to its policy".
- Examples back to `dc+sd-jwt` and the -23 data, re-signed (KB-JWT `iat` 1793905352). History: "working on Éric Vyncke's Discuss".

Changes in -26 (6 November 2026):

- Section 7.1 cites the IANA IPv4 and IPv6 Special-Purpose Address Registries instead of RFC 6890 (Éric Vyncke's comment).
- Section 2.2.2.2: duplicate sentence "Holders and Verifiers can treat the SD-JWT VC as a credential of these types." removed.
- No other change apart from the dates.

Context from earlier revisions, per the document history in Appendix C: the general HTTP retrieval section and SSRF generalisation arrived in -19, the `aka_vcts` claim in -18, the `x5c`/`iss` clarification and the first RFC 7800 note in -20, and -23 was "some minor fixes".

## Impact Analysis

- Upstream: The draft depends on RFC 9901 for the SD-JWT format and processing, RFC 7519 and RFC 7515 for JWT and JWS rules, RFC 5280 for `x5c` chain validation, RFC 7800 for `cnf`, and RFC 9110 and RFC 9111 for HTTP retrieval and caching. Since -24 it updates RFC 7800: the second paragraph of RFC 7800 Section 3, which requires `sub` or `iss` alongside `cnf`, is nullified for all JWTs (Section 2.2.2.3.1). The status list reference is normative since -22.
- Downstream: Wallets, issuers and verifiers that implement SD-JWT VC, and ecosystem profiles that define `vct` values, Type Metadata and additional key discovery mechanisms (Sections 2.2.2.1 and 2.5). Once published, the RFC 7800 update also applies to any JWT profile that uses `cnf`. IANA is asked to register `vct`, `vct#integrity`, `aka_vcts`, the media type `application/dc+sd-jwt` and the well-known URI suffix `jwt-vc-issuer` (Section 9), with placeholder document references still in the -26 text.
- Compatibility: A recipient that supports both JWT VC Issuer Metadata and `x5c` must check that its policy, not the credential, picks the mechanism, and that it does not pass on an unauthenticated `iss` as the Issuer under `x5c` (Section 2.5, since -24). Take test vectors from -25 or -26 (same examples), not -24, whose encoded examples use `typ` `vc+sd-jwt`. The -26 examples verify (hands-on log). The draft's `typ` value is `dc+sd-jwt`, and the transitional note about `vc+sd-jwt` was removed in -19.
