# Spec Notes

## References

Normative references listed in the draft (Section 10.1):

- [I-D.ietf-oauth-status-list] draft-ietf-oauth-status-list-21.
- RFC 2119, RFC 8174 (BCP 14), RFC 2397 (data URL scheme), RFC 3986 (URI syntax), RFC 5646 (language tags), RFC 6890 (special-purpose IP address registries).
- RFC 7515 (JWS), RFC 7517 (JWK), RFC 7519 (JWT), RFC 7800 (proof-of-possession key semantics), RFC 8615 (well-known URIs).
- RFC 9110 (HTTP Semantics), RFC 9111 (HTTP Caching), RFC 9901 (SD-JWT).
- [W3C.CSS-COLOR] CSS Color Module Level 3, [W3C.SRI] Subresource Integrity.

Informative references (Section 10.2):

- [EUDIW.ARF], [IANA.JWT], [IANA.MediaTypes], [IANA.well-known], [NIST-BLOG.VDCE], [OWASP_SSRF].
- RFC 6901 (JSON Pointer), RFC 9205 (Building Protocols with HTTP), RFC 9535 (JSONPath), [UAX9] (Unicode Bidirectional Algorithm).

## Key Changes

Changes in -23 relative to -22 (`diff.txt`):

- Expiry date and draft date refreshed (4 May 2027 and 31 October 2026).
- Example signatures regenerated in Figures 7, 8, 10, 26 and the Appendix A.1 examples. The KB-JWT `iat` and `sd_hash` values changed in Figures 8, 26 and 27.
- Editorial: `text_color` wording in Section 5.5.1.1, "in by [RFC8615]" in Section 9.3, trailing slash removed from the OWASP URL.
- Su-hyeon Forten Lee added to the acknowledgements. The history entry for -23 reads "some minor fixes".
- No visible change to normative requirements.

Context from earlier revisions, per the document history in Appendix C: the general HTTP retrieval section and SSRF generalisation arrived in -19, the `aka_vcts` claim in -18, and the `x5c`/`iss` clarification and the RFC 7800 note in -20.

## Impact Analysis

- Upstream: The draft depends on RFC 9901 for the SD-JWT format and processing, RFC 7519 and RFC 7515 for JWT and JWS rules, RFC 7800 for `cnf`, and RFC 9110 and RFC 9111 for HTTP retrieval and caching. Section 2.2.2.3 departs from the RFC 7800 Section 3 requirement for `sub` or `iss`, and no `Updates:` header is shown in the material. The status list reference is normative since -22.
- Downstream: Wallets, issuers and verifiers that implement SD-JWT VC, and ecosystem profiles that define `vct` values, Type Metadata and additional key discovery mechanisms (Sections 2.2.2.1 and 2.5). IANA is asked to register `vct`, `vct#integrity`, `aka_vcts`, the media type `application/dc+sd-jwt` and the well-known URI suffix `jwt-vc-issuer` (Section 9), with placeholder document references still in the text.
- Compatibility: -23 has no visible protocol change, so implementations of -22 should interoperate. Only test vectors differ. The draft's `typ` value is `dc+sd-jwt`, and the transitional note about `vc+sd-jwt` was removed in -19. Any outcome of the open DISCUSS on Section 2.2.2.3 is not known.
