# Context

## Trigger

The subject was picked as "Diff active WG draft: draft-ietf-wimse-workload-creds-03". The note recorded with it says: reorganised structure, stricter trust-anchor binding, new proof-audience section and dropped single-identifier rule, all in a core WG draft. Datatracker states are Active, I-D Exists and WG Document. One correction to that note: the draft still requires exactly one Workload Identifier per credential (Section 4, Section 5.1 `sub`, Section 6.1). What was dropped is the paragraph that told deployments how to handle several labels for the same runtime.

## Why This Matters

The draft is the credential layer for the WIMSE companion documents on mutual TLS, the Workload Proof Token and HTTP message signatures (Section 1). Changes to how a recipient validates a WIT (Section 5.1.3), how trust anchors are bound to a trust domain (Section 3) and how audience is checked (Section 5.2) apply to every protocol that reuses these credentials. The working group chair asked the list on 30 October 2026 to flag anything substantive that needs more discussion, because it is a core document.

## Open Questions

- Does Section 5.1.3 give enough for interoperable validators without an explicit `exp`, algorithm or `iss` check?
- Is the shorter Section 4 enough once the guidance on stable versus instance identities is gone?
- How do callers and callees learn the expected callee identifier and their own audience value (Sections 1.2, 5.2)?
- Is `EdDSA` still accepted in `cnf.jwk.alg` next to `Ed25519`? The draft does not say.
- Which changes does the working group regard as substantive? The staged mail does not show any discussion beyond the announcement.
