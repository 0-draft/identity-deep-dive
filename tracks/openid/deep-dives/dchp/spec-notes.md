# Spec Notes

## References

Normative references in `draft/digital-credentials-harmonized-presentation.md` at `4ddd238` (the list ends with "To be completed"):

- ISO/IEC 18013-5, Mobile driving licence (mDL) application.
- RFC 5280 (X.509 certificate and CRL profile), used for the Authority Key Identifier in issuer matching.
- RFC 7515 (JWS), for the `x5c` header of the SD-JWT VC Issuer-signed JWT.
- RFC 9901 (SD-JWT) and draft-ietf-oauth-sd-jwt-vc (SD-JWT VC).

All of these were added by pull request #57 (commit `13ca44e` adds RFC 7515). The text also cites, outside that list, RFC 8610 (CDDL, including sockets), RFC 9052 (`COSE_Sign`, `COSE_Key`, `COSE_Encrypt`), RFC 9360 (`COSE_X509`), RFC 8949 Section 4.2 (deterministic CBOR), RFC 8943 (`full-date`), draft-ietf-cose-hpke, ISO/IEC TS 23220-2 (`age_over_NN`) and the ISO/IEC Directives, Part 2, for the "shall/should/may/can" verbal forms.

The README links ISO/IEC 18013-5 (<https://www.iso.org/standard/69084.html>), OpenID for Verifiable Presentations 1.0 (<https://openid.net/specs/openid-4-verifiable-presentations-1_0.html>) and the Editor's Copy (<https://openid.github.io/dchp/digital-credentials-harmonized-presentation-editors-copy.html>).

## Key Changes

Merged:

- #61 (4 November 2026, 8 commits, closes issue #46): `credential_type: tstr` became `credential_types: [ + tstr ]` (key 2). It also defines how a request is processed when the array has n entries.
- #57 (9 November 2026, 23 commits, closes issues #21, #22 and #36): the "Credential Formats" clause and its ten requirements on a format definition; the ISO mdoc and SD-JWT VC annexes; the `$formatExtensions` and `$CredentialData` sockets; the `CredentialItem.format` to `credential_format` rename (same map key); `dc+sd-jwt` instead of `vc+sd-jwt`; new normative references. Its commits also moved SD-JWT VC path semantics to issue #52 (`c029b57`), used the RFC 5280 name for the authority key identifier (`4fae852`) and dropped a mapping of `support_no_cryptographic_binding` to `DocRequestInfo` (`dfd7dd4`).
- #29 (16 August 2026): the initial proposal, accepted as a starting point "but it doesn't yet constitute consensus on its full content". #7, #11 and #15 are repository and build housekeeping.

Open, as of 11 November 2026 (what each diff does):

- #64: a "CBOR Encoding" clause. It requires RFC 8949 Section 4.2.1 core deterministic encoding, forbids NaN and infinities, and says transcripts are never transmitted.
- #65: when reader authentication uses X.509, the certificate goes in an `x5chain` in the protected header of the `COSE_Signature` (RFC 9360). The first certificate holds the reader key.
- #74: an abbreviations table for M (Mandatory), C (Conditional) and O (Optional).
- #76 (closes issue #75): aligns the CDDL with the prose. It renumbers `ChannelBinding`, adds `cce_handover`, renames `oidc4vp_*` to `openid4vp_*` and `nfcv2` to `cce`, fixes `controlled_id` to `controller_id`, drops the unused `full-date`, and writes `* (int / tstr) => any` with parentheses.
- #77 (closes issues #69 and #70): the `Envelope.credentials` map becomes an array, `CredentialItem` gains `query_refs` (key 3), `CredentialRef` is renamed `QueryRef`, and `allow_multiple` controls whether several items may answer one query.
- #81 (closes issue #67): "reader" becomes "verifier", including `reader_auth` to `verifier_auth` and `ReaderTransactionTranscript` to `VerifierTransactionTranscript`.
- #83 (fixes issue #58): snake_case for `scenario_sets` and `credential_queries`, and similar casing fixes. The working group called it editorial "since map keys are ints".
- #85 (refs issue #72): a Security Considerations clause reading "To be completed" and the OIDF Notices appendix, so that a WG Draft can be published.

Closed without merge:

- #84: opened and closed within a minute on 4 November 2026. #85 came from the same branch (`72-required-sections`) with the same title and the same diff.
- #59, #73 and #82: earlier rounds of the casing fix. #59 and #73 were closed in favour of the next one, and #82 was replaced by #83 because of merge conflicts.

## Impact Analysis

- Upstream: the mdoc annex reuses ISO/IEC 18013-5 structures (`Document`, `DeviceAuth`, `SessionTranscript`, `KeyAuthorizations`). Two editor's notes tie it to the second edition of 18013-5: issuer identifiers follow "the same rule as the `IssuerIdentifiers` structure being defined in the second edition", and non-key-bound mdocs follow the "changes proposed for its DIS ballot" (issue #56). The SD-JWT VC annex builds on RFC 9901 and draft-ietf-oauth-sd-jwt-vc. Issue #53 asks whether `vct` inheritance should work as it does in OpenID4VP. Issue #52 wants the `path` aligned with the OpenID4VP and 18013-5 claims path pointer.
- Downstream: wallets and verifiers that want one model for proximity and online presentation, and protocols that would carry these messages. The `ChannelBinding` already has fields for OpenID4VP and the Digital Credentials API. The repository names no implementations.
- Compatibility: requests built before #61 put a text string at key 2 and fail against the array type. SD-JWT VC queries built before #57 use `vc+sd-jwt`. If #77 merges, responses built before it no longer match the `Envelope` CDDL. If #76 merges, `ChannelBinding` keys built from the CDDL on `main` change, and so do the transcript bytes and the hash values.
