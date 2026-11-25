# Hands-on Log

## Environment

- Runtime: Python 3.15.2
- Tooling: `cryptography` 50.0.2 (Ed25519, ECDSA P-256)
- Versions: draft-miao-wimse-http-signature-test-vectors-00 (IETF archive text, fetched 26 November 2026)

## Steps

1. Copy the five test keys, WIT-A and the P-01 message from Sections 3 and 4.1 of the -00 text into `vectors/lab1.py`, with the RFC 8792 folds removed.
2. Run `python3 -I vectors/lab1.py > vectors/lab1.log`.
3. Read `vectors/lab1.log`: one line per key, the WIT-A check, and the two P-01 re-signing results.

## Results

- 26 November 2026: every key derives from its seed as Section 3 states. For issuer, svcA, svcB and other, `d` is the base64url of `SHA-256("s01-validation-vectors:<name>")` and the public `x` matches. For svcC, the scalar `SHA-256("s01-validation-vectors:svcC") mod (n-1) + 1` gives the published `d`, `x` and `y`.
- WIT-A verifies under the issuer key, and its payload has `iat` T0-60, `exp` T0+3600 and `cnf.jwk` set to vec-a-key, as Section 3 says.
- Re-signing the P-01 base with svcA's key gives the published Signature value byte for byte only when the `workload-identity-token` line carries the full WIT-A text. With the placeholder `[WIT-A，§2 全文]` as printed, the value differs.

## Failure Modes

- Building the signature base with the placeholder exactly as printed in the -00 text: the P-01 signature does not match, although Section 2 says the placeholder is retained verbatim in the signed material.

## Next Actions

- Run Lab 2 against a running server to record the HTTP status for each vector.
- Run Lab 3 (N-17, N-18, N-20) against a real server.
