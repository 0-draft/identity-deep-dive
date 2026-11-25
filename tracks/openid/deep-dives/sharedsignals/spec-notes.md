# Spec Notes

## References

Documents in the repository at `d8f89ab`:

- Shared Signals Framework 1.0 (Final) and 1.1 (draft), in kramdown-rfc Markdown
- CAEP 1.0 (Final) and 1.1 (draft), in kramdown-rfc Markdown
- CAEP Interoperability Profile 1.0, draft 01, in kramdown-rfc Markdown
- RISC 1.0 (Final), in xml2rfc XML

SSF's normative references include SET (RFC 8417), Subject Identifiers for SETs (RFC 9493), push delivery (RFC 8935), poll delivery (RFC 8936), JWT (RFC 7519), JWK (RFC 7517), OAuth 2.0 (RFC 6749), well-known URIs (RFC 8615), HTTP Semantics (RFC 9110), OpenID Connect Core, CAEP and RISC. JWS (RFC 7515) and JWA (RFC 7518) are not among them; #355 would add both. The profile's normative references point to SSF 1.0 Final, not to the 1.1 draft.

## Key Changes

- #310 (merged 13 November 2026): moves the 1.0 texts unchanged into `SSF_1.0/`, `CAEP_1.0/` and `RISC_1.0/`, and creates `SSF_1.1/` and `CAEP_1.1/` from them. SSF 1.1 changes only its title and `docname`. CAEP 1.1 also adds the `https://schemas.openid.net/secevent/caep/event-type/v1.1` base URI for new or updated events and keeps 1.0 events valid.
- #368 (merged 17 November 2026): deletes the profile's "Event Signatures" section ("All events MUST be signed using the `RS256` algorithm with a minimum of 2048-bit keys."). No other file changes.
- #356 (closed unmerged 16 November 2026): the alternative that would have required JWS signing, forbidden `none` and kept 2048-bit RSA keys without fixing RS256.
- #343 (merged 21 July 2026): prepares the profile's Draft-01 for OIDF member review.
- #349 (merged 1 September 2026): adds the Risk Level Change use case to the profile.
- #315 (merged 17 February 2026): adds Receiver requirements to the profile.
- Open proposals: #355 SET signing algorithm negotiation (SSF 1.1), #367 CORS for `ssf-configuration` and `jwks_uri` (SSF 1.1), #369 JSON `null` in stream configuration (SSF 1.1), #366 complex subjects in the profile's Event Subjects, #363 well-known paths per version in the profile, #362 agent and workload subjects (SSF and CAEP 1.0 files, conflicting), #329 an `unmanaged` device status (CAEP 1.1).

## Impact Analysis

- Upstream: SSF profiles SET and its delivery RFCs and uses JWT and JWK. It does not reference JWS directly and does not require SETs to be signed (Section 7.1: `jwks_uri` "MUST be specified if the Transmitter intends to generate signed JWTs").
- Downstream: Transmitter and Receiver implementers of SSF and CAEP, and deployers following the CAEP Interoperability Profile.
- Compatibility: SSF 1.1 currently has the same rules as 1.0, and CAEP 1.1 keeps 1.0 event types. No compatibility policy for future 1.1 changes is written down. For the profile, #368 removes a constraint, so a Transmitter that signs with RS256 still conforms; a Receiver that accepted only RS256 because of the profile may now meet Transmitters that use other algorithms.
