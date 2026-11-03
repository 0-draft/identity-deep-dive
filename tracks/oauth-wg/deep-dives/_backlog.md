# OAuth WG Backlog (2026-11-03)

- generated_at_utc: `2026-11-03T01:00:27+00:00`

- [ ] `draft-ietf-oauth-sd-jwt-vc` score=125 updated=2026-10-31T18:37:09Z
- [ ] `draft-ietf-oauth-client-id-metadata-document` score=90 updated=2026-11-02T22:02:56Z
- [ ] `draft-ietf-oauth-rfc7523bis` score=90 updated=2026-11-02T17:24:26Z
- [ ] `draft-ietf-oauth-identity-assertion-authz-grant` score=90 updated=2026-10-31T00:32:39Z
- [ ] `draft-ietf-oauth-deferred-token-response` score=83 updated=2026-10-31T16:12:16Z
- [ ] `draft-ietf-oauth-v2-1` score=83 updated=2026-10-31T04:16:32Z
- [ ] `draft-ietf-oauth-delegate-sd-jwt` score=83 updated=2026-10-30T12:38:29Z
- [ ] `draft-ietf-oauth-rfc8725bis` score=65 updated=2026-08-31T18:37:20Z
- [ ] `draft-ietf-oauth-identity-chaining` score=65 updated=2026-08-21T20:25:31Z
- [ ] `draft-ietf-oauth-status-list` score=65 updated=2026-08-13T20:11:32Z
- [ ] `draft-ietf-oauth-attestation-based-client-auth` score=58 updated=2026-10-18T17:33:02Z
- [ ] `draft-ietf-oauth-transaction-tokens` score=56 updated=2026-08-21T11:57:16Z
- [ ] `draft-ietf-oauth-first-party-apps` score=50 updated=2026-08-26T14:40:16Z
- [ ] `draft-ietf-oauth-spiffe-client-auth` score=45 updated=2026-11-02T17:35:55Z
- [ ] `draft-ietf-oauth-rar-metadata-remediation` score=20 updated=2026-08-23T20:29:29Z
- [ ] `draft-ietf-oauth-refresh-token-expiration` score=20 updated=2026-07-06T17:53:06Z
- [ ] `draft-ietf-oauth-security-topics-update` score=20 updated=2026-07-06T06:41:36Z

<!-- triage:start -->
## Triage

Moved by this week's material. candidates.json and the site list raised candidates first and lowered ones last.

- **high** `draft-ietf-oauth-client-id-metadata-document`: -03 adds a normative client authentication section, iss in responses, fetch failure rules and three merged PRs.
- **high** `draft-ietf-oauth-deferred-token-response`: -01 restructures the draft with substrate invariants, a new deferred_interactive mode and new editors; also cited as the answer to ID-JAG consent.
- **high** `draft-ietf-oauth-identity-assertion-authz-grant`: -06 adds new normative behaviour (client auth at IdP, invalid_request, mTLS binding, new metadata) and a large rewrite.
- **high** `draft-ietf-oauth-sd-jwt-vc`: IESG ballot has a DISCUSS (RFC 7800 override, no Updates: tag) and a supporting No Objection with SSRF and x5c comments.
- **high** `draft-ietf-oauth-spiffe-client-auth`: -03 makes client_id optional, ties client identification to CIMD and adds replay and trust-bundle security text.
- **high** `draft-ietf-oauth-v2-1`: Seven new issues and 31 closed, several tagged ietf-127, including MUST vs SHOULD in §3.2.3 and invalid_client.
- **low** `draft-ietf-oauth-delegate-sd-jwt`: PR #14 adds a worked example and generator, so implementers can check their output against it.
- **low** `draft-ietf-oauth-transaction-tokens`: Only a new implementation-report issue (#373) with one comment; no text change.

<!-- triage:end -->
