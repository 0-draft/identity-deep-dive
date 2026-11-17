# Interop Checklist

- [ ] Check which of the 1.0 and 1.1 drafts the implementation targets, and confirm that each merged change (for example #744, #782, #790, #800) is applied in that version's text.
- [ ] Test age_over_nn claim matching (#800) with a query for one age threshold against a credential that holds a different threshold, and record what the wallet returns.
- [ ] Test `vct` matching and `doctype` matching (#744, #803), including the `vct_values` and `doctype_value` parameters, with a matching and a non-matching credential.
- [ ] Return an SD-JWT VC in `vp_token` as defined after #782, and confirm the verifier accepts it. Also test a credential without Holder Binding (#783).
- [ ] Confirm that an empty object in a VP Token is not accepted by the verifier as an error signal (#745).
- [ ] Send a request with unsupported `transaction_data` and check that the wallet follows the terminate/reject/return behaviour of #790. Re-check after #808 is resolved.
- [ ] Send verifier metadata that is invalid and check that the wallet returns `invalid_request` (#801).
- [ ] Check that client metadata lists `encrypted_response_enc_values_supported` (#802) and that the wallet picks an encryption method from it.
- [ ] For each Client Identifier Prefix, check whether a Request URI response may be unsigned (#788), and reject an unsigned one where the prefix requires a signed request.
- [ ] Check the signed Request Object example in Section 5.4 against the final text (#809) before using it as a test vector.
- [ ] Test nonce handling with a short nonce (#722) and confirm the wallet or verifier rejects or flags it as the final text requires.
- [ ] Over the DC API, check that `expected_origins` processing and platform-specific origins follow #719 and #761.
- [ ] Verify that a direct post response is matched to the correct user session (#734), including a response replayed from another session.
- [ ] Check that the `openid_federation` prefix is used consistently in examples (#776) and cross-references (#775).
- [ ] Run the OpenID conformance tests for wallets and verifiers linked from the README against the target version.
