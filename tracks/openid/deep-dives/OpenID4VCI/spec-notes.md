# Spec Notes

## References

Normative references named in the drafts at `21ffd6c` that matter most for interop:

- OAuth 2.0 (RFC 6749), on which the whole API is built; Rich Authorization Requests (RFC 9396) for `authorization_details`; Pushed Authorization Requests (RFC 9126); DPoP (RFC 9449).
- Pre-final dependencies pinned to specific revisions (1.0 Section 14.7): OpenID Federation 1.0 draft -43, SD-JWT VC draft -11, Attestation-Based Client Authentication draft -07 and Token Status List draft -12. 1.1 adds OAuth 2.0 for First-Party Applications draft -04 (1.1 Section 15.9).
- OpenID4VP, used inside Interactive Authorization for the presentation step (1.1 Section 6.2.1.1).
- s2s: mutual TLS (RFC 8705) on every endpoint, Problem Details (RFC 9457) for errors, and `Sunset` (RFC 8594) for API version retirement (s2s Sections 5.1, 5.3 and 5.4).

## Key Changes

Checked against each pull request diff.

- 1.0 errata `-19`: terminating `/` removal restored in Section 12.2.2 (#775); Section 13.6.3 "Transaction Code Guessing" added (#686).
- 1.1 Interactive Authorization (Section 6): profile of First-Party Applications with the Authorization Challenge Endpoint (#736); 403 instead of 401 (#781); URN interaction types (#712).
- 1.1 `auth_session`: required only if the interaction type says so (#706); the Wallet sends the most recent value (#710); with DPoP, the AS MUST associate it with the DPoP public key (#803).
- 1.1 `auth_via_web`: the Wallet uses each `request_uri` once (#704) and sends `state` when it runs concurrent sessions (#797).
- 1.1 Credential Response: `credential_metadata` (#721), `credential_dataset_id` and `credential_dataset_tag` (#472). Token Error Response: `invalid_tx_code` (#686).
- 1.0 and 1.1: `202 Accepted` in the deferred example (#722); omit `cryptographic_binding_methods_supported` when no key binding is needed (#714).
- s2s: first draft (#753), snake_case properties (#809). Open: identifier renames (#810), deferred credentials (#816).
- Open on 1.0 and 1.1: `issuer_redirect_uri` (#759), `nonce` conditions in proof types (#678). Open on 1.1: `error_code` wording fix (#819).

## Impact Analysis

- Upstream: Interactive Authorization depends on the First-Party Applications draft, pinned at -04; its error format (`error`, Section 5.2.2) is why #819 is a wording fix. The SD-JWT VC format profile depends on a pinned pre-final SD-JWT VC revision.
- Downstream: HAIP 1.0 profiles OpenID4VCI (OpenID DCP WG specifications page). Wallets and issuers built on 1.0 Final are affected by the errata metadata rule. Those that also follow 1.1 are affected by `invalid_tx_code` and the Credential Dataset parameters.
- Compatibility: #775 changes the metadata URL for identifiers that end in `/`, and #744 calls it technically breaking. #686 moves the wrong-Transaction-Code error from `invalid_grant` (1.0) to `invalid_tx_code` (1.1). #819 does not change the wire format. The s2s renames change JSON names in a draft that has no stable version.
