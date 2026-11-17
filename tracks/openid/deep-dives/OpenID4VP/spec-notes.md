# Spec Notes

## References

The staged material is a README and a pull-request list, not a draft, so it lists no normative or informative references. Items it mentions by name:

- JAR (JWT-Secured Authorization Request), mentioned in the title of #798.
- SD-JWT VC, mentioned in #782 and #726.
- The Digital Credentials API (DC API), mentioned in #761.
- DCQL, mentioned in #647.
- OpenID Federation, implied by the `openid_federation` prefix in #776.

The reference lists of the 1.0 and 1.1 drafts are not shown and need to be read from the drafts.

## Key Changes

The repository holds two specifications: OpenID for Verifiable Presentations 1.0 and 1.1 working-group drafts, both built from the main branch. The README gives only pull-request titles. Merged: age_over_nn claims matching (#800), `invalid_request` for verifier metadata (#801), `encrypted_response_enc_values_supported` in client metadata (#802), terminate/reject/return behaviour (#790), `vct` and `doctype` matching (#744), JAR fallback text (#798), security considerations for client_metadata (#735), normative SD-JWT VC encoding in `vp_token` (#782), a VC without Holder Binding returned directly (#783), unsigned Request URI responses for some prefixes (#788), DC API origin guidance (#761), empty object not usable as an error (#745), untrusted input text (#748, #759), expected_origins processing (#719), `intent_to_retain` when absent (#730), nonce entropy (#722) and matching a direct post request to the user session (#734). Open: #808, #809, #803, #726, #804. Closed without merge: #647.

## Impact Analysis

- Upstream: the material does not show the upstream specifications' text. Titles suggest dependence on JAR, SD-JWT VC, the DC API and OpenID Federation.
- Downstream: wallets, verifiers and the conformance tests linked from the README are affected by the matching rules, error behaviour and `vp_token` encoding. The material does not list any specific downstream implementation.
- Compatibility: the material does not say which changes are breaking. #803 mentions adding text to 1.0, and #726 mentions a version inconsistency in 1.0 final, so a reviewer should check how each change applies to each version.
