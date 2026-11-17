# OAuth WG Backlog (2026-11-17)

- generated_at_utc: `2026-11-17T20:58:16+00:00`

- [ ] `draft-ietf-oauth-sd-jwt-vc` score=125 updated=2026-11-16T10:45:13Z
- [ ] `draft-ietf-oauth-rfc8725bis` score=90 updated=2026-11-17T15:06:04Z
- [ ] `draft-ietf-oauth-status-list` score=83 updated=2026-11-12T21:31:43Z
- [ ] `draft-ietf-oauth-identity-chaining` score=83 updated=2026-11-12T02:07:35Z
- [ ] `draft-ietf-oauth-client-id-metadata-document` score=73 updated=2026-11-02T22:02:56Z
- [ ] `draft-ietf-oauth-identity-assertion-authz-grant` score=73 updated=2026-10-31T00:32:39Z
- [ ] `draft-ietf-oauth-v2-1` score=66 updated=2026-10-31T04:16:32Z
- [ ] `draft-ietf-oauth-delegate-sd-jwt` score=66 updated=2026-10-30T12:38:29Z
- [ ] `draft-ietf-oauth-transaction-tokens` score=62 updated=2026-08-21T11:57:16Z
- [ ] `draft-ietf-oauth-deferred-token-response` score=58 updated=2026-10-31T16:12:16Z
- [ ] `draft-ietf-oauth-attestation-based-client-auth` score=58 updated=2026-10-18T17:33:02Z
- [ ] `draft-ietf-oauth-first-party-apps` score=50 updated=2026-08-26T14:40:16Z
- [ ] `draft-ietf-oauth-spiffe-client-auth` score=28 updated=2026-11-02T17:35:55Z
- [ ] `draft-ietf-oauth-rar-metadata-remediation` score=20 updated=2026-08-23T20:29:29Z
- [ ] `draft-ietf-oauth-refresh-token-expiration` score=20 updated=2026-07-06T17:53:06Z
- [ ] `draft-ietf-oauth-security-topics-update` score=20 updated=2026-07-06T06:41:36Z

<!-- triage:start -->
## Triage

Moved by this week's material. candidates.json and the site list raised candidates first and lowered ones last.

- **high** `draft-ietf-oauth-client-id-metadata-document`: Fresh implementation report with editor replies. It raises possible additions on SSRF/DNS rebinding, cache bounds, RFC 8252 and scope handling.
- **high** `draft-ietf-oauth-delegate-sd-jwt`: PR #15 restructures where security claims live in the KB-SD-JWT and defines their delegation semantics.
- **high** `draft-ietf-oauth-identity-assertion-authz-grant`: New issue #161 reports a conflict between the §4.3.3 and §4.5 rules, and #121 was closed this week.
- **high** `draft-ietf-oauth-sd-jwt-vc`: -27 changes how type matching works: types come only from vct and aka_vcts, and extends no longer adds types.
- **low** `draft-ietf-oauth-v2-1`: Only a citation fix (PR 284) landed; no protocol change.

<!-- triage:end -->
