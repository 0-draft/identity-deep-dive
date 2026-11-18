# Spec Notes

## References

Normative references as listed in the draft (Section 12.1):

- [I-D.ietf-oauth-status-list] Token Status List, draft-ietf-oauth-status-list-21
- RFC 2119 and RFC 8174 (BCP 14), RFC 5234 (ABNF), RFC 6749 (OAuth 2.0)
- RFC 7515 (JWS), RFC 7519 (JWT), RFC 7800 (proof-of-possession key semantics)
- RFC 8032 and RFC 8037 (Ed25519 in JOSE), RFC 8785 (JCS)
- RFC 9068 (JWT access tokens), RFC 9396 (Rich Authorization Requests), RFC 9449 (DPoP)
- RFC 9728 (Protected Resource Metadata), RFC 9864 (fully-specified algorithms)

Informative references (Section 12.2) include:

- Capability lineage: Macaroons, Biscuit, RFC 2693 (SPKI)
- Related drafts: draft-niyikiza-oauth-attenuating-agent-tokens-02, draft-coetzee-oauth-spt-txn-tokens-03, draft-sweeney-wimse-credential-delegation-01, draft-ietf-wimse-aims-00, draft-ietf-wimse-identifier-04, draft-reece-wimse-cross-org-delegation-02, draft-jackson-wimse-evaluation-04, draft-hamr-oauth-agent-delegation-03, draft-ietf-oauth-identity-chaining-17
- New in -03: draft-mcguinness-oauth-actor-profile-01, draft-mw-oauth-actor-chain-02, draft-gilda-audit-agent-audit-record-02
- Others: RFC 7009 (revocation), RFC 7942 (implementation status), RFC 8693 (Token Exchange), RFC 8705 (mTLS), RFC 9964 (ML-DSA)

## Key Changes

- Section 1.2 added, covering the relationship to the OAuth "act"-claim actor drafts.
- Table 1 gains a row, and a paragraph follows it, saying Principal standing is not established by the chain or the request (Section 6.1).
- Section 6.4 separates the binding gap from the recording gap and cites draft-gilda-audit-agent-audit-record. No anchor topology is mandated.
- Section 10 drops the requests to register "del_depth", "del_max_depth" and "par_hash". The "Agent Delegation Constraint Types" registry request stays.
- Step 5 of Section 6 requires now less than exp.
- Section 7 specifies DPoP holder binding only. mTLS is left to a later revision.
- Section 4.4 records a rule that a child adding a detail type its parent lacked is treated as widening, for a later revision. Under -03 it is malformed.
- Appendix B describes a set of thirty-six vector files, up from thirty-five, and the -01 set of twenty stays unchanged. A new Appendix C, "Changes Since -02", is added, and the -01 change list moves to Appendix D.
- Informative references are bumped: draft-hamr-oauth-agent-delegation -02 to -03, draft-ietf-wimse-identifier -03 to -04, and draft-niyikiza-oauth-attenuating-agent-tokens -01 to -02.
- Section 11 reports library versions attenu-guard 0.22.0 and attenu-guard-ts 0.16.0 (up from 0.20.0 and 0.14.0), says their built-in signer still uses "EdDSA", and relays, as its author reports it, a 2026-10-20 run of the Cred conformance harness against the thirty-five -02 vectors with 20 passes, 5 failures and 10 declared gaps. No run against all thirty-six vectors has been reported. The attenu-guard repository's v0.22.0 tag (released 2026-10-27) has 36 JSON files in src/attenu_guard/vectors/draft02 (35 at v0.21.0) and 20 -01 files in src/attenu_guard/vectors; the Cred result was not reproduced.

## Impact Analysis

- Upstream: builds on RFC 9068, RFC 9396, RFC 9449, RFC 7800, RFC 8785 and RFC 9864, and on draft-ietf-oauth-status-list for revocation. It says it is designed as the attenuation mechanism satisfying requirements R1 and R5 of draft-reece-wimse-cross-org-delegation, and that it follows draft-ietf-wimse-aims on "client_id" and "sub". Its claim names overlap with draft-niyikiza-oauth-attenuating-agent-tokens.
- Downstream: gateways and enforcement points that verify agent chains, auditors that re-check recorded chains, and companion documents for scope vocabulary and audit records. The draft expects a companion document for scope vocabulary (Section 4.5), and draft-gilda-audit-agent-audit-record is cited for retaining root-key material.
- Compatibility: -03 defines no transition mode for -01-shaped chains. The 20 -01 vectors do not conform to the new revision and are kept byte-stable. The now less than exp change and the removal of mTLS are behavior changes from -02. The "del_max_depth" semantics differ from the niyikiza draft, so the same depth values can pass there and fail step 3 here (Section 10; Section 4.3 of draft-niyikiza-oauth-attenuating-agent-tokens-02 allows a child's del_depth up to its parent's del_max_depth).
