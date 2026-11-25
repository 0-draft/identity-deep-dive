# Interop Checklist

- [ ] Check which signing algorithms a Receiver accepts now that the profile (after #368) no longer fixes `RS256`, and that it rejects any algorithm outside its configured allow-list.
- [ ] Check that a profile Transmitter still publishes its current signing keys at `jwks_uri` and that the Receiver fetches them from there (profile Sections 2.3.3 and 2.4.2).
- [ ] Check that every SET carries `typ` `secevent+jwt`, has no `sub` or `exp` claim, and has an `iss` matching the stream configuration (SSF 1.0 Sections 4.1.1, 4.1.2, 4.1.6 and 4.1.7).
- [ ] Check that each SET a profile Transmitter sends has exactly one event in its `events` claim (profile Section 2.7.1).
- [ ] Proposal (#355, open): if it merges as written, create streams with a supported `set_signing_alg`, without it, and with an unsupported value, and check the `400` response and the `alg` the Transmitter returns.
- [ ] Proposal (#366, open): if it merges as written, send complex subjects built from `email` and `iss_sub` and check that profile Receivers accept them.
- [ ] Proposal (#369, open): if it merges as written, send JSON `null` for an OPTIONAL stream configuration property and check that the other side treats it as absent.
- [ ] Proposal (#367, open): if it merges as written, fetch the Transmitter Configuration Metadata and the JWK Set from a browser origin and check the CORS headers, and check that endpoints needing authorization refuse cross-origin requests.
- [ ] Proposal (#363, open): if it merges as written, check that a Transmitter serving both `1_0` and `1_0-ID1` Receivers publishes `/.well-known/ssf-configuration` and `/.well-known/sse-configuration` separately, each with the right `spec_version`.
