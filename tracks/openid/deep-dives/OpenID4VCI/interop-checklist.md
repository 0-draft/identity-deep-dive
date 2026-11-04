# Interop Checklist

Section numbers are for 1.0 unless marked 1.1 or s2s, at commit `21ffd6c`.

- [ ] Confirm which text each peer implements: 1.0 Final, the 1.0 errata draft, 1.1, or s2s. They differ on the items below.
- [ ] Form the metadata URL for `https://<host>/tenant` and `https://<host>/tenant/`. The errata text and 1.1 give `/.well-known/openid-credential-issuer/tenant` for both; 1.0 Final has no rule for the terminating `/`, so read literally the second keeps it (Section 12.2.2, #744, #775).
- [ ] Send a Credential Offer by value (`credential_offer`) and by reference (`credential_offer_uri`), and check that the Wallet rejects an offer that carries both (Section 4.1).
- [ ] Send a Pre-Authorized Code Token Request with a wrong `tx_code`: expect `invalid_grant` from a 1.0 AS and `invalid_tx_code` from a 1.1 AS (1.0 Section 6.3, 1.1 Section 7.3).
- [ ] Send repeated wrong `tx_code` values and check that the AS invalidates the Pre-Authorized Code after its limit and then returns `invalid_grant` (errata Section 13.6.3).
- [ ] When the issuer has a Nonce Endpoint, check that a `jwt` proof without `nonce` is rejected with `invalid_proof`, and one with a stale `c_nonce` is rejected with `invalid_nonce` (Section 8.3.1.2, Appendix F.1).
- [ ] For a configuration without `cryptographic_binding_methods_supported`, check that the Wallet omits `proofs` and the issuer accepts the request (Section 14.2, #714).
- [ ] Return a deferred response and check the Wallet honours `202`, `transaction_id` and `interval`, then gets the credential from the Deferred Credential Endpoint (Sections 8.3 and 9).
- [ ] 1.1 Interactive Authorization: check that `insufficient_authorization` comes with 403 Forbidden and that the error key is `error`, as in the examples, not `error_code` (Section 6.2.1, #781, #819).
- [ ] 1.1: check that the Wallet always sends the most recent `auth_session`, and that, with DPoP, the AS rejects that `auth_session` with a different DPoP key (Section 6.2.1, #710, #803).
- [ ] 1.1 `auth_via_web`: check that the Wallet uses each `request_uri` once, sends `state` when it runs concurrent sessions, and that the AS rejects an expired `request_uri` (Section 6.2.1.2, #704, #797).
- [ ] 1.1: if `expected_origins` is present in the presentation request, check that it holds only the derived Origin of the Authorization Challenge Endpoint and that the Wallet checks it (Section 6.2.1.1).
- [ ] 1.1: when `credential_dataset_id` is present, check that `credential_dataset_tag` is present too, and that the Wallet replaces stored credentials when the tag changes (Sections 9.3 and 15.4).
- [ ] s2s: check that both servers use mTLS, send `Api-Version`, and answer an unsupported version with HTTP 400 and Problem Details (s2s Sections 5.1 and 5.3).
