# Interop Checklist

Section numbers are for 1.0 unless marked 1.1 or s2s, at commit `41c8c66`.

- [ ] Confirm which text each peer implements: 1.0 Final, the 1.0 errata draft, 1.1, or s2s. They differ on the items below.
- [ ] Form the metadata URL for `https://<host>/tenant` and `https://<host>/tenant/`. The errata text and 1.1 give `/.well-known/openid-credential-issuer/tenant` for both; 1.0 Final has no rule for the terminating `/`, so read literally the second keeps it (Section 12.2.2, #744, #775).
- [ ] Send a Credential Offer by value (`credential_offer`) and by reference (`credential_offer_uri`), and check that the Wallet rejects an offer that carries both (Section 4.1).
- [ ] Send a Pre-Authorized Code Token Request with a wrong `tx_code`: expect `invalid_grant` from a 1.0 AS and `invalid_tx_code` from a 1.1 AS (1.0 Section 6.3, 1.1 Section 7.3).
- [ ] Send repeated wrong `tx_code` values and check whether the AS follows the errata SHOULDs: an error saying the code is invalid while under the limit, then invalidating the Pre-Authorized Code and returning `invalid_grant` once the limit is exceeded (errata Section 13.6.3). These are SHOULDs, so record the behavior rather than fail it. Section 6.3 still lists a wrong Transaction Code under `invalid_grant` and 1.0 has no other code for it, so expect `invalid_grant` in both cases and check `error_description` for the distinction.
- [ ] When the issuer has a Nonce Endpoint, check that a `jwt` proof without `nonce` is rejected with `invalid_proof`, and one with a stale `c_nonce` is rejected with `invalid_nonce` (Section 8.3.1.2, Appendix F.1).
- [ ] For a configuration without `cryptographic_binding_methods_supported`, check that the Wallet omits `proofs` and the issuer accepts the request (Section 14.2, #714).
- [ ] Return a deferred response and check the Wallet honours `202`, `transaction_id` and `interval`, then gets the credential from the Deferred Credential Endpoint (Sections 8.3 and 9).
- [ ] 1.1 Interactive Authorization: check that `insufficient_authorization` comes with 403 Forbidden and that the error key is `error`, as in the examples, not `error_code` (Section 6.2.1, #781, #819).
- [ ] 1.1: check that the Wallet always sends the most recent `auth_session`, and that, with DPoP, the AS rejects that `auth_session` with a different DPoP key (Section 6.2.1, #710, #803).
- [ ] 1.1 `auth_via_web`: check that the Wallet uses each `request_uri` once, sends `state` when it runs concurrent sessions, and that the AS rejects an expired `request_uri` (Section 6.2.1.2, #704, #797).
- [ ] 1.1: if `expected_origins` is present in the presentation request, check that it holds only the derived Origin of the Authorization Challenge Endpoint and that the Wallet checks it (Section 6.2.1.1).
- [ ] 1.1: when `credential_dataset_id` is present, check that `credential_dataset_tag` is present too, and that the Wallet replaces stored credentials when the tag changes (Sections 9.3 and 15.4).
- [ ] 1.1: check which spelling each peer uses for the Interactive Authorization identifiers: the `ia:` or `iae:` binding prefix, `ia_post` or `iae_post`, `authorization_challenge_endpoint` or `interactive_authorization_endpoint`, `require_interactive_authorization` or `require_interactive_authorization_request`, and the mdoc `OpenID4VCIIAEHandover` label (#811, open).
- [ ] 1.1: check the presentation binding value per format: SD-JWT VC KB-JWT `aud` (text says derived Origin, example shows the endpoint URL), JWT VC JSON `aud` and LDP VC `domain` (endpoint URL with `ia:`), mdoc handover (endpoint URL without `ia:`). An AS that accepts more than one value loses the anti-relay check (#812, open).
- [ ] s2s: check that both servers use `wallet_id` and `credential_id`, not the pre-#810 `session_id` and `credential_instance_id`.
- [ ] s2s: check that both servers use mTLS, send `Api-Version`, and answer an unsupported version with HTTP 400 and Problem Details (s2s Sections 5.1 and 5.3).
