# OAuth WG Backlog (2026-11-11)

- generated_at_utc: `2026-11-11T19:38:32+00:00`

- [ ] `draft-ietf-oauth-sd-jwt-vc` score=118 updated=2026-11-06T19:07:22Z
- [ ] `draft-ietf-oauth-rfc8725bis` score=83 updated=2026-11-06T22:32:52Z
- [ ] `draft-ietf-oauth-status-list` score=73 updated=2026-11-03T19:29:28Z
- [ ] `draft-ietf-oauth-client-id-metadata-document` score=73 updated=2026-11-02T22:02:56Z
- [ ] `draft-ietf-oauth-identity-assertion-authz-grant` score=73 updated=2026-10-31T00:32:39Z
- [ ] `draft-ietf-oauth-v2-1` score=66 updated=2026-10-31T04:16:32Z
- [ ] `draft-ietf-oauth-delegate-sd-jwt` score=66 updated=2026-10-30T12:38:29Z
- [ ] `draft-ietf-oauth-identity-chaining` score=65 updated=2026-08-21T20:25:31Z
- [ ] `draft-ietf-oauth-transaction-tokens` score=64 updated=2026-08-21T11:57:16Z
- [ ] `draft-ietf-oauth-attestation-based-client-auth` score=58 updated=2026-10-18T17:33:02Z
- [ ] `draft-ietf-oauth-first-party-apps` score=50 updated=2026-08-26T14:40:16Z
- [ ] `draft-ietf-oauth-deferred-token-response` score=46 updated=2026-10-31T16:12:16Z
- [ ] `draft-ietf-oauth-spiffe-client-auth` score=28 updated=2026-11-02T17:35:55Z
- [ ] `draft-ietf-oauth-rar-metadata-remediation` score=20 updated=2026-08-23T20:29:29Z
- [ ] `draft-ietf-oauth-refresh-token-expiration` score=20 updated=2026-07-06T17:53:06Z
- [ ] `draft-ietf-oauth-security-topics-update` score=20 updated=2026-07-06T06:41:36Z

<!-- triage:start -->
## Triage

Moved by this week's material. candidates.json and the site list raised candidates first and lowered ones last.

- **high** `draft-ietf-oauth-attestation-based-client-auth`: A detailed critical review of -12 questions its structure and DPoP/RFC 7521 reuse.
- **high** `draft-ietf-oauth-client-id-metadata-document`: 11 issues closed and a new response_types issue (#131) this week, with PRs adding a Client Authentication section.
- **high** `draft-ietf-oauth-delegate-sd-jwt`: PR #15 restructures where security claims live in the KB-SD-JWT and defines their delegation semantics.
- **high** `draft-ietf-oauth-identity-assertion-authz-grant`: Two new issues (#159, #160) on jwt-dpop and client authentication point to open design questions.
- **high** `draft-ietf-oauth-sd-jwt-vc`: PR #457 changes how credential types are matched (vct and aka_vcts only, no extends matching), with ISO/IEC 18013-5 about to cite a dated draft.
- **low** `draft-ietf-oauth-transaction-tokens`: PR #374 fixes a missing IANA registration for the required req_wl claim, a small editorial fix.

<!-- triage:end -->
