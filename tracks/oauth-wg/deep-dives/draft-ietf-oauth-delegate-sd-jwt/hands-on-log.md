# Hands-on Log

## Environment

- Runtime: Python 3.15.2, run as `python3 -I`
- Tooling: `cryptography` 50.0.2 (Ed25519 signing and verification), the Python standard library, nothing else
- Versions: draft-ietf-oauth-delegate-sd-jwt-00 and RFC 9901, read from local `.txt` copies (`draft-ietf-oauth-delegate-sd-jwt-00.txt`, `rfc9901.txt`). Run on 18 November 2026. PR #15 in the draft's repository is still open, so this log follows the -00 text.

## Steps

1. The draft has no worked examples, so `vectors/delegate_labs.py` mints its own tokens. Every key is Ed25519, derived from a fixed label. Salts come from labels, every timestamp is fixed and the verifier clock is 1794960000 (2026-11-18T00:00:00Z). Ed25519 signatures are deterministic, so two runs give byte-identical output. ES256 was not used because ECDSA signatures change on every run.
2. The script holds two verifiers written from the text. `rfc9901_verify` follows RFC 9901 Section 4 (compact format and ABNF), 7.1 and 7.3, and knows nothing of delegation. `dsd_verify` is a prototype of draft Section 6, with the format rules of Sections 5.1.1, 5.1.3 and 5.1.4. It can skip the hash checks of Section 6 steps 3.3/3.4 (`link_hash`) or step 5.3 (`kb_sd_hash`) to model a lax verifier for Lab 3.
3. Run `python3 -I vectors/delegate_labs.py > vectors/delegate_labs.log`. Each case prints `PASS` or `FAIL` against an expected `accept` or `reject`, with the rejection reason. The run ends with `ALL OK` and exit status 0 only if every case matches and the self-test passes.
4. Check that the script can fail. The self-test flips one bit of the Issuer signature (both verifiers must reject), zeroes the `sd_hash` inside a KB-SD-JWT (rejected), and tells the harness that a tampered token should be accepted. That last line must print `FAIL`, and the script checks that it does.
5. Run the script twice and compare the outputs with `cmp` to confirm the log is reproducible.

How the tokens are built (choices where -00 is open are in Failure Modes):

- Issuer SD-JWT: `typ` `example+sd-jwt`, visible `iss`, `iat`, `exp`, `vct` and `cnf.jwk` (Holder key), with `given_name`, `family_name` and `card_last4` as object-property Disclosures (RFC 9901 Sections 4.1, 4.2.1).
- KB-SD-JWT: signed with the Holder key, `typ` `kb-sd-jwt+kb`. Its top-level payload has the KB-JWT claims `iat`, `aud`, `nonce`, plus `sd_hash` or `issuer_jwt_hash`, `_sd_alg` and `delegate_payload` (Section 5.1.4). `delegate_payload` is `[{"...": <digest>}]`, and the Delegate Payload Disclosure is `[salt, {iss, exp, cnf, max_amount, _sd}]` (Section 5.1.3). `merchant` and `item` are Disclosures nested in it.
- Compact form: `<Issuer JWT>~<D>~<D>~<D>~~<KB-SD-JWT>~<DP>~<D>~<D>~<KB-JWT>`, which splits into 10 components with one empty component before the KB-SD-JWT (Section 5.1.1). The final KB-JWT is signed with the agent key from the Delegate Payload `cnf`, and its `sd_hash` covers `<KB-SD-JWT>~<DP>~<D>~<D>~` (Sections 5.1.3, 6 step 5.3).

## Results

The output is in `vectors/delegate_labs.log`: 46 cases, 0 unexpected, self-test OK, `ALL OK`. Two runs give the same bytes.

- Lab 1 (one delegation):
  - The RFC 9901 verifier accepts the plain SD-JWT+KB baseline, so it is not just rejecting everything.
  - It rejects both the dSD-JWT+KB and the dSD-JWT (trailing `~`). It stops at the RFC 9901 Section 4 ABNF, because the empty component before the KB-SD-JWT is not a `DISCLOSURE`. A parser that drops the empty and JWT components first still rejects, at RFC 9901 Section 7.1 step 5, because the Delegate Payload Disclosures are not referenced by any digest in the Issuer-signed JWT.
  - The Section 6 prototype accepts the dSD-JWT+KB and returns the Issuer payload and the Delegate Payload (`max_amount` 50, `merchant` `shop-a`). It accepts the dSD-JWT when Key Binding is not required and rejects it when Key Binding is required (step 5.1).
  - The prototype also rejects: a plain SD-JWT+KB (no KB-SD-JWT), two empty components or none before the KB-SD-JWT (5.1.1), a KB-SD-JWT signed by the agent key instead of the Holder `cnf` (step 3.1), `typ` `kb+jwt` or `kb+sd-jwt` in a dSD-JWT+KB (step 4.2), and a final KB-JWT signed by the Holder key (step 5.2).
  - With two `delegate_payload` elements under one signature (Section 5.1.4), disclosing one is accepted and disclosing both is rejected (step 3.2). The Delegate Holder may leave out `merchant` and `item`, and the result still verifies (Section 4.1).
- Lab 2 (`sd_hash` and `issuer_jwt_hash`, `given_name` dropped from the Issuer SD-JWT):

  | Case | `sd_hash` | `issuer_jwt_hash` |
  | --- | --- | --- |
  | All three Issuer Disclosures | accept | accept |
  | `given_name` dropped by the Delegate Holder | reject (step 3.3) | accept, Verifier sees `family_name`, `card_last4` |
  | `given_name` removed from the finished dSD-JWT+KB in transit | reject (step 3.3) | accept |
  | All Issuer Disclosures dropped | reject (step 3.3) | accept, no Issuer claims |
  | A Disclosure the Issuer never signed added | reject (RFC 9901 7.1 step 5) | reject (RFC 9901 7.1 step 5) |

  With `issuer_jwt_hash`, no signature in the dSD-JWT+KB covers the Issuer Disclosures. The KB-SD-JWT hashes only the Issuer-signed JWT (Section 5.1.4), and the final KB-JWT's `sd_hash` covers only the final KB-SD-JWT and its Disclosures (Section 5.1.3, Section 6 step 5.3). Section 4.1 makes `issuer_jwt_hash` the way a Holder lets the Delegate Holder omit Issuer Disclosures, so omission itself is intended. What the lab adds is that the omission is not limited to the Delegate Holder: anyone who handles the finished presentation can strip Issuer Disclosures and it still verifies. Adding Disclosures is still caught. In a plain RFC 9901 SD-JWT+KB, the KB-JWT `sd_hash` covers the Disclosures presented. With `sd_hash`, the Delegate Holder must present exactly the Issuer Disclosures the Holder selected, no fewer.
- Lab 3 (SD-JWT A for card `1111` and SD-JWT B for card `2222`, both with the same Holder `cnf`; delegation A sets `max_amount` 50, delegation B sets 5000; both delegate to the same agent key):
  - Both chains verify on their own.
  - SD-JWT A with KB-SD-JWT B is rejected by the full Section 6 verifier: step 3.3 with `sd_hash` and step 3.4 with `issuer_jwt_hash`. A lax verifier that checks only the signature under the preceding `cnf` accepts it and outputs card `1111` with `max_amount` 5000. This is the mix-up that Section 8.1 warns about.
  - The other direction: since the agent key is reused too, attaching chain B's final KB-JWT to chain A is rejected at step 5.3 and accepted when 5.3 is skipped.
  - Control: with different Holder keys for A and a third credential C, the lax verifier already rejects the swap on the signature (step 3.1). So the hash check matters exactly when the `cnf` is reused, as Section 8.1 says.
  - When the same SD-JWT is delegated twice with the same Disclosures, both KB-SD-JWTs carry the same `sd_hash`, so the hash link cannot tell them apart. With Key Binding, the agent cannot present agent-2's KB-SD-JWT (step 5.2 rejects it). As a dSD-JWT without Key Binding, anyone who holds KB-SD-JWT #2 can present it.

## Failure Modes

These are places where -00 can be read more than one way. The script does what is listed here.

- Where the claims go. Section 5.1.4 moves "all claims that are expected to be found in the issuer-signed JWT Payload except the `_sd_alg` claim" into the Delegate Payload, but also says a KB-SD-JWT MUST meet all the requirements of a KB-JWT. The script keeps the KB-JWT claims (`iat`, `aud`, `nonce`, `sd_hash`/`issuer_jwt_hash`) plus `_sd_alg` and `delegate_payload` in the top-level payload, and puts `iss`, `exp` and `cnf` in the Delegate Payload. PR #15 would move `cnf`, `exp` and `nbf` to the top level.
- A single `delegate_payload` element. Section 5.1.4 requires Disclosures only when there is more than one element. Section 5.1.3 describes the Delegate Payload as an Array Disclosure, and Section 6 step 3.2 asks for "exactly one disclosed element". The script always wraps the Delegate Payload in a Disclosure, and the verifier counts the elements left after RFC 9901 Section 7.1 processing.
- `aud` and `nonce` of a KB-SD-JWT. Section 6 step 3 does not check them against the Verifier, and a KB-SD-JWT is addressed to the Delegate Holder. The script checks that they are present and have the right type, and checks `aud` and `nonce` only on the final KB-JWT. PR #15 would say that they apply to the delegation step.
- Input to `issuer_jwt_hash`. Section 5.1.4 says it is a digest of "only the preceding Issuer-signed jwt or KB-SD-JWT+KB". The script hashes the US-ASCII compact JWS, with no trailing `~`.
- Input to `sd_hash` in a KB-SD-JWT. The script uses `<preceding JWT>~<D.1>~...~<D.N>~` as in RFC 9901 Section 4.3.1, without the extra empty component that separates the chain links.
- Validity of the Delegate Payload. Step 3.1 says to treat the Delegate Payload as the JWT Payload. The script applies RFC 9901 Section 7.1 step 6 (`exp`, `nbf`) to it.
- "Both directions" in Section 8.1. The script reads it as the signature under the preceding `cnf` (step 3.1) and the hash of the preceding token (steps 3.3/3.4). Lab 3 shows that the signature alone passes when the `cnf` is reused.
- "Section 4.3.1" and "Section 7.3" in Sections 5.1.4 and 6 are read as RFC 9901 sections, as noted in the README.
- The `iat` window for the final KB-JWT is 300 seconds, our choice for RFC 9901 Section 7.3 step 5.e.

## Next Actions

- Chains with two or more KB-SD-JWTs (Section 5.1.1), including a non-final `kb+sd-jwt` that step 3.5 must reject.
- The JSON Serialization (Section 5.1.2) and the OpenID4VP `delegate` transaction data type (Section 7.1).
- Re-run the labs after PR #15 merges, and compare the tokens with the example proposed in PR #14.
- Raise upstream that, with `issuer_jwt_hash`, the Issuer Disclosures in a dSD-JWT+KB are covered by no signature.
