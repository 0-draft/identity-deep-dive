# Hands-on Log

## Environment

- Runtime: Python 3.15.2
- Tooling: `cryptography` 50.0.2 (Ed25519, ECDSA P-256 with RFC 6979 deterministic signing), `gh` to fetch the draft source
- Versions: draft-ietf-wimse-http-signature-08 (tag `draft-ietf-wimse-http-signature-08` in ietf-wg-wimse/draft-ietf-wimse-s2s-protocol), issue #419 vectors with the 7 November 2026 regenerated values

## Steps

1. Fetch the `sigs-*.txt` include files used by the Section 3.7 examples from the `draft-ietf-wimse-http-signature-08` tag into a local `includes/` directory (`gh api repos/ietf-wg-wimse/draft-ietf-wimse-s2s-protocol/contents/<file>?ref=draft-ietf-wimse-http-signature-08 -H "Accept: application/vnd.github.raw"`).
2. Run `python3 -I vectors/verify_419.py includes/ > vectors/verify_419.log`. The vector inputs and test keys from issue #419 are written into the script, so the include files are only needed for the Section 3.7 example check.
3. Read the summary table at the end of the log, and the per-vector notes for N-01, N-04, N-06, N-07, N-09 and N-15.

## Results

- Section 0 of the log: every test key derives from `SHA-256("s01-validation-vectors:<name>")` (svcC reduced mod n-1, plus 1), and the three WITs verify under the issuer key.
- Section 1: the script rebuilds all 8 published signatures (P-01 to P-05, both P-06 signatures, N-15) byte for byte.
- Most negative vectors are this repository's reconstructions of the change the issue describes, not the issue's bytes. spec-notes lists which vectors used which inputs.
- No vector disagreed with its expected outcome. 22 accept/reject vectors and 4 behaviour vectors matched. N-17 and N-20 were not scored. The findings are in spec-notes, "Test Vector Re-run".

## Failure Modes

- Taking the issue body's original P-01, P-02, P-06 and N-15 signatures instead of the 7 November values: they verify only over an `@query` without the leading `?`.
- Reporting N-04 as a signature failure: the signature is valid, and only the recomputed digest fails.

## Next Actions

- Score N-17 and N-20 against a real server, where the error body and the order of checks can be observed.
- Check the WIT validation in the script against the workload credentials draft text. The script follows this repository's reading of it and has not been compared clause by clause.
