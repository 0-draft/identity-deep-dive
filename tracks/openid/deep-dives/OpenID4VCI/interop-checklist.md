# Interop Checklist

This list is derived from pull request titles only. Confirm each item against the draft text.

- [ ] Check which draft each peer implements (1.0, 1.1 or s2s) before testing anything else.
- [ ] Form the Credential Issuer Metadata URL from an identifier with and without a terminating `/` and confirm both sides agree (#775).
- [ ] Send an Interactive Authorization error and check whether the field is `error` or `error_code` (#819).
- [ ] Check that the pre-authorized code flow returns `invalid_tx_code` for a wrong transaction code (#686).
- [ ] Check proof `nonce` handling both when a Nonce endpoint exists and when it does not (#678).
- [ ] When DPoP is used, verify that `auth_session` is bound; when another binding exists, verify that omitting `auth_session` is accepted (#803, #706).
- [ ] Run two concurrent sessions and verify that `state` keeps them apart, and that `auth_session` is the most recent value in the session (#797, #710).
- [ ] Verify that `request_uris` are unique across requests (#704).
- [ ] Check the 202 response for deferred issuance, including its HTTP reason phrase and the later retrieval (#722).
- [ ] Check the HTTP status codes of Interactive Authorization responses against the first party apps draft-4 values (#781).
- [ ] If Credential Offer carries `issuer_redirect_uri`, check that wallets that do not know it ignore or reject it consistently (#759, open).
- [ ] For s2s, check Document properties are snake_case and identifier model names match the agreed list (#809, #810).
- [ ] Check how an issuer signals that cryptographic key binding is not required, and that wallets do not send a proof then (#714).
