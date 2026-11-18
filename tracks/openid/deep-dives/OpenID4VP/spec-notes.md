# Spec Notes

## References

Normative references in the 1.0 Final text that matter most for interop:

- OAuth 2.0 (RFC 6749), with RFC 9700 recommendations where applicable (Section 5); JAR (RFC 9101) for Request Objects, `request_uri` and the `oauth-authz-req+jwt` type (Section 5); OAuth 2.0 Multiple Response Type Encoding Practices for Response Modes (Section 5.2).
- JOSE: JWS (RFC 7515) for signed requests and the `x5c`, `kid` and `jwt` headers; JWE (RFC 7516) and JWA (RFC 7518) for encrypted responses (Section 8.3).
- Credential formats: SD-JWT and SD-JWT VC, ISO/IEC 18013-5 for mdoc, W3C VCDM (Appendix B).
- OpenID Federation, normatively referenced by the `openid_federation` Client Identifier Prefix: "Processing rules given in [OpenID.Federation] MUST be followed", metadata comes from the Trust Chain and `client_metadata` MUST be ignored (Section 5.9.3). It is also a `trusted_authorities` type in DCQL (Section 6.1.1.3). The dependency is in the normative text, not only in the name of #776, which fixed an example.
- W3C Digital Credentials API (Appendix A), DID Core (`decentralized_identifier` prefix) and SIOPv2 (Appendix C).
- Pre-final dependencies pinned to specific revisions (Section 13.4): OpenID Federation 1.0 draft -43, SIOPv2 draft -13, SD-JWT draft -22, SD-JWT VC draft -09 and Fully-Specified Algorithms draft -13. Issue #659 notes that the rendered normative reference for SD-JWT VC points at -10; #726 (open) would fix it.
- The errata draft adds the WHATWG HTML definition of an Origin (#719) and two formal security analyses (errata Sections 14.1 and A.5).

## Key Changes

Checked against each pull request's diff and file list.

- Both the 1.0 errata draft and 1.1: `age_over_NN` data element selection for mdoc, a SHOULD (#800, merged 11 November 2026, errata Section B.2.5); termination means no response, and unsupported `transaction_data` gives no VP Token and SHOULD give `invalid_transaction_data` (#790); no empty VP Token (#745); compact SD-JWT only (#782); W3C VC without Holder Binding returned directly (#783); `alg: none` Request URI response for prefixes that require unsigned requests (#788); MUST fall back to GET for unsupported `request_uri_method` values (#798); "Source of Verifier Metadata" (#735); `invalid_request` for a format outside `vp_formats_supported` (#801); `encrypted_response_enc_values_supported` listed in Verifier metadata (#802); `nonce` SHOULD have 128 bits of entropy (#722); `state` RECOMMENDED (#734); `expected_origins` matched by simple string comparison (#719); `intent_to_retain` when absent (#730); `origin` prefix cross-reference (#775); `openid_federation` in the `invalid_request` example (#776); `ldp_vc` example (#787); untrusted input (#748 for 1.1, #759 for 1.0).
- 1.1 only: `vct_values` and `doctype_value` matching (#744), platform-specific application Origins (#761, Section A.5.1), HPKE `session_info` (#703) and the HPKE exception for `encrypted_response_enc_values_supported` (#698), and no VP Token as an Access Token (#702, Section 14.6).
- Open: #803 (#744's text for 1.0), #808 (relax `transaction_data`), #809 (Section 5.4 example, 1.1 only), #726 (SD-JWT VC version), #804 (Selectively Disclosable Claim, 1.1 only).
- Closed without merge: #647 (DCQL injection consideration). Closed on 18 June 2026 for lack of a contribution agreement and progress; generalized by #748 and #759.

## Impact Analysis

- Upstream: OpenID4VP depends on pre-final SD-JWT VC, SD-JWT, OpenID Federation and SIOPv2 revisions (Section 13.4). #744 relies on `aka_vcts` from SD-JWT VC draft -15, per its description. The `age_over_NN` rule defers to ISO 18013-5 Section 7.2.5.
- Downstream: Section 3 says the specification needs profiling. `data/landscape-sources.json` lists HAIP 1.0 as Final (approved December 2025). Wallets, Verifiers and the OpenID conformance tests (Section 14.7) are affected by the errata changes listed above.
- Compatibility: Final and errata peers can differ on `alg: none` Request URI responses (#788), unknown `request_uri_method` values (#798), empty VP Tokens (#745) and the returned `age_over_NN` identifier (#800). 1.0 and 1.1 differ on `vct_values` inheritance until #803 merges.
