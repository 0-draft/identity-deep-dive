# Spec Notes

## References

The staged material does not include the drafts, so their normative and informative reference lists are not available. The material mentions these related documents by name only:

- The OpenID first party apps draft (FPA), on which Interactive Authorization is built (#736, #781 refers to FPA draft-4).
- DPoP, referenced in #803.
- VCDM 2 with JOSE, the subject of the closed #699.

## Key Changes

The list comes from pull request titles only.

- First draft of OpenId4VCI-S2S merged (#753), followed by snake_case Document properties (#809) and build rules (#799); identifier model names (#810) and deferred credential (#816) are open.
- Interactive Authorization built on the first party apps draft (#736); `error` instead of `error_code` in its error response is open (#819).
- Session binding: `auth_session` required when DPoP is used (#803), optional if another binding exists (#706), `state` binds concurrent sessions (#797).
- Credential dataset version (#472), metadata in the credential response (#721), `invalid_tx_code` (#686), terminating `/` removed when forming the metadata URL (#775).
- Open: `issuer_redirect_uri` in Credential Offer (#759), `nonce` conditions in proof types (#678).

## Impact Analysis

- Upstream: The Interactive Authorization work depends on the first party apps draft and its numbering (FPA draft-4, #781); DPoP is referenced for session binding (#803). The material does not show more.
- Downstream: Wallets and issuers implementing 1.0 or 1.1, and systems using the s2s draft, are affected. The material names no implementations.
- Compatibility: The `error_code` to `error` rename (#819) and the s2s renames (#809, #810) can break earlier drafts, and the metadata URL change (#775) affects what an issuer serves. Whether these are breaking is not stated in the material.
