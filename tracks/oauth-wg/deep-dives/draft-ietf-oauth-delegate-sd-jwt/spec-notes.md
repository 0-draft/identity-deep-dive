# Spec Notes

## References

Normative references listed in Section 10.1:

- OpenID for Verifiable Presentations 1.0 ([OIDF.OID4VP], 9 July 2025), used in Section 7.1.
- RFC 2119.
- RFC 6838, for media type registration.
- RFC 7519, JWT.
- RFC 9901, Selective Disclosure for JSON Web Tokens, the base specification.

Informative references listed in Section 10.2:

- IANA JSON Web Token Claims registry.
- IANA Media Types registry.
- RFC 2046.

## Key Changes

Revision -00 is the "Initial Working Group Draft", adopted from draft-gco-oauth-delegate-sd-jwt. The pre-adoption history lists -01 (editorial fixes and `kb+sd-jwt+kb` renamed to `kb-sd-jwt+kb`) and -00 (initial version) (Appendix C). Comparing the repository tags draft-gco-oauth-delegate-sd-jwt-00 and draft-ietf-oauth-delegate-sd-jwt-00 also shows normative changes: exactly one empty component before every KB-SD-JWT, including between chained ones (Section 5.1.1), digests over the equivalent Compact Serialization for the JSON Serialization (Section 5.1.2), a REQUIRED `sd_hash` in the final Delegate KB-JWT (Section 5.1.3), and a rewritten Section 6 that fixes the `typ` values and rejects a dSD-JWT without Key Binding when Key Binding is required. What the draft introduces:

- The dSD-JWT and dSD-JWT+KB formats, in Compact and JSON Serialization (Sections 5.1, 5.1.1, 5.1.2).
- The KB-SD-JWT, with `typ` values `kb+sd-jwt` and `kb-sd-jwt+kb`, a `delegate_payload` claim and an `issuer_jwt_hash` claim as an alternative to `sd_hash` (Section 5.1.4).
- A verification procedure for the chain (Section 6).
- An OpenID4VP `transaction_data` type `delegate` (Section 7.1).
- IANA requests for the `issuer_jwt_hash` claim and for the media types `application/kb+sd-jwt` and `application/kb-sd-jwt+kb` (Appendix A).

Open PR #15 in the draft's repository would move the security claims (`cnf`, `exp`, `nbf` and others) from the Delegate Payload into the base KB-SD-JWT payload and add a section on their meaning along the chain.

## Impact Analysis

- Upstream: The draft depends on RFC 9901 for SD-JWT, Disclosure and KB-JWT processing, on RFC 7519 for JWT, and on OpenID4VP for the delegation transport in Section 7.1. It reuses RFC 9901 Section 7.1 for each link, and RFC 9901 Sections 4.3.1 and 7.3 for `sd_hash` and KB-JWT checks (written as bare "Section 4.3.1" and "Section 7.3" in the -00 text).
- Downstream: Wallets, Verifiers and agent frameworks that handle SD-JWT presentations would need to parse chained tokens and apply the Section 6 checks. The draft names AI agents as a use case (Abstract, Section 1).
- Compatibility: A dSD-JWT does not match the SD-JWT or SD-JWT+KB grammar in RFC 9901 Section 4, because a Disclosure there cannot be empty and an SD-JWT+KB ends in a single JWT. The draft does not describe negotiation. The earlier `kb+sd-jwt+kb` name was replaced by `kb-sd-jwt+kb` before adoption. `delegate_payload` is not in the IANA request in Appendix A.
