# Spec Notes

## References

Normative references listed in Section 10.1:

- OpenID for Verifiable Presentations 1.0 ([OIDF.OID4VP]), used in Section 7.1.
- RFC 2119.
- RFC 6838, for media type registration.
- RFC 7519, JWT.
- RFC 9901, Selective Disclosure for JSON Web Tokens, the base specification.

Informative references listed in Section 10.2:

- IANA JSON Web Token Claims registry.
- IANA Media Types registry.
- RFC 2046.

## Key Changes

No `diff.txt` is staged. Revision -00 is the "Initial Working Group Draft", adopted from draft-gco-oauth-delegate-sd-jwt. The pre-adoption history lists -01 (editorial fixes and `kb+sd-jwt+kb` renamed to `kb-sd-jwt+kb`) and -00 (initial version) (Appendix C). What the draft introduces:

- The dSD-JWT and dSD-JWT+KB formats, in Compact and JSON Serialization (Sections 5.1, 5.1.1, 5.1.2).
- The KB-SD-JWT, with `typ` values `kb+sd-jwt` and `kb-sd-jwt+kb`, a `delegate_payload` claim and an `issuer_jwt_hash` claim as an alternative to `sd_hash` (Section 5.1.4).
- A verification procedure for the chain (Section 6).
- An OpenID4VP `transaction_data` type `delegate` (Section 7.1).
- IANA requests for the `issuer_jwt_hash` claim and for the media types `application/kb+sd-jwt` and `application/kb-sd-jwt+kb` (Appendix A).

## Impact Analysis

- Upstream: The draft depends on RFC 9901 for SD-JWT, Disclosure and KB-JWT processing, on RFC 7519 for JWT, and on OpenID4VP for the delegation transport in Section 7.1. It reuses RFC 9901 Section 7.1 for each link.
- Downstream: Wallets, Verifiers and agent frameworks that handle SD-JWT presentations would need to parse chained tokens and apply the Section 6 checks. The draft names AI agents as a use case (Abstract, Section 1).
- Compatibility: A dSD-JWT is not a valid RFC 9901 SD-JWT presentation because of the empty component `~~` and the changed KB-JWT, and the draft does not describe negotiation. The earlier `kb+sd-jwt+kb` name was replaced by `kb-sd-jwt+kb` before adoption. `delegate_payload` is not in the IANA request in Appendix A.
