# Spec Notes

## References

Normative references listed in Section 12.1:

- [I-D.ietf-oauth-rfc8725bis] JSON Web Token Best Current Practices (draft revision 10), new in 03 and replacing RFC 8725.
- [I-D.ietf-wimse-mutual-tls] Workload Authentication Using Mutual TLS (draft revision 03).
- [WIMSE-ID] Workload Identifier (draft-ietf-wimse-identifier revision 04).
- RFC 2119, RFC 8174, RFC 5234, RFC 7515, RFC 7517, RFC 7518, RFC 7519, RFC 7800, RFC 7942, RFC 9110.
- RFC 9525 (Service Identity in TLS), new in 03.

Informative references listed in Section 12.2:

- [I-D.ietf-wimse-arch] (revision 08), [I-D.ietf-wimse-wpt] (revision 02), [I-D.ietf-wimse-http-signature] (revision 08), [I-D.ietf-oauth-transaction-tokens] (revision 11).
- [I-D.ietf-oauth-status-list] (revision 21), RFC 6960 (OCSP) and RFC 9864 (fully-specified algorithms), all new in 03.
- RFC 9457, and the IANA registries for HTTP fields, JOSE algorithms, JWT claims and media types.
- RFC 8414 was removed from the references.

## Key Changes

- Structure: the section "Use In Other Protocols" is removed, Sections 5 and 6 are retitled "Application-Layer Credentials" and "Transport-Layer Credentials", a Section 5.2 on audience and a Section 5.1.3 on WIT validation are added, and the Security Considerations are renumbered (new Section 9.2).
- Section 1.2: the mapping API requirement is replaced by caller and callee conditions and a reference to RFC 9525 for server identity.
- Section 3: validation only against anchors bound to the trust domain in the Workload Identifier; the issuer must be known and preconfigured; the explicit prohibition on `iss`-based key lookup is removed in favour of Section 9.1 and the removal of `iss`-based key distribution.
- Section 4: the paragraph on deployments with several labels for one runtime (a stable service identity and an instance, say) is removed. It put the identity used for the access decision in the one credential and forbade encoding a second identifier for correlation. Exactly one identifier per credential is kept.
- Section 5.1: `sub` and `jti` definitions reworded, `jti` tied to deny-list or status list deployments, `typ` guidance now cites the RFC 8725 successor draft.
- Section 5.3: HTTP 401 allowed when a `WWW-Authenticate` mechanism exists.
- Section 9: revocation stance for WIT and WIC, exposure after deprovisioning, key-protection wording, and the clarification that WIT and PoP are not used for mutual TLS.
- Examples use `Ed25519` in `cnf.jwk.alg`; the example WIT was re-signed. The implementation status gains a wimsey entry.

## Impact Analysis

- Upstream: depends on the WIMSE architecture draft for terminology and trust domains, on the WIMSE Workload Identifier draft for identifier syntax and the `wimse` URI scheme, and on the JWT best-practices successor draft. A change in any of these drafts can affect this one, because three normative references are still Internet-Drafts.
- Downstream: the mutual TLS, WPT and HTTP signature drafts supply the proof of possession and must define audience handling that satisfies Section 5.2. Section numbers they cite from this draft may have moved. Identity server and SPIFFE-style implementations that issue WITs and WICs are the main implementers.
- Compatibility: a WIT with `typ` of `wit+jwt`, `sub` and `cnf.jwk.alg` should still validate. Behaviour that changes is `iss`-driven key lookup (no longer supported), the algorithm name in examples (`Ed25519`), the 401 guidance and the removed mapping requirement. The draft does not say whether `EdDSA` remains accepted.
