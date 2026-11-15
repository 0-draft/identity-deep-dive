# Hands-on Log

## Environment

- Runtime: Python 3.15.2
- Tooling: `cryptography` 50.0.2 (ECDSA P-256 verification), `curl` to fetch the draft text
- Versions: draft-ietf-oauth-sd-jwt-vc-24, -25 and -26 (`.txt` from `https://www.ietf.org/archive/id/`), run on 15 November 2026

## Steps

1. Fetch the drafts: `curl -sfL -o draft-ietf-oauth-sd-jwt-vc-26.txt https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-26.txt` (and -24, -25).
2. Run `python3 -I vectors/verify_examples.py draft-ietf-oauth-sd-jwt-vc-26.txt 7 8 10 24 26` for each revision. The script reads the compact serialization above each figure caption, takes the Issuer keys from Figure 14, verifies the ES256 Issuer signature, looks up the SHA-256 digest of every Disclosure in the payload `_sd` arrays, array `...` entries and nested Disclosures, and for a KB-JWT verifies it under `cnf.jwk` and recomputes `sd_hash` over the SD-JWT up to the last `~`.
3. Check that the script can fail: flipping one character of a Disclosure in Figure 7 gives `digests-not-found=1`, and flipping one character of the Figure 10 signature gives `issuer-sig=FAIL`.

## Results

- The output is in `vectors/verify_examples.log`. All three revisions print `ALL OK`.
- -26: Figures 7, 8, 10, 24 and 26 have `typ` `dc+sd-jwt`, the Issuer signatures verify with `doc-signer-05-25-2022` (only Figures 7 and 8 name it in `kid`), 9, 2, 2, 28 and 3 Disclosures all have their digest in place, and the KB-JWTs in Figures 8 and 26 verify with a matching `sd_hash` (`iat` 1793905352).
- -25 gives the same output as -26.
- -24 also verifies, but every encoded example has `typ` `vc+sd-jwt`, the KB-JWT `iat` is 1724705969 (26 August 2024), and Figure 24 has 21 Disclosures instead of 28.

## Failure Modes

- Taking examples from -24: their `typ` is `vc+sd-jwt`, which the -24 text no longer allows.
- Assuming a `kid` in every example: Figures 10, 24 and 26 have none, so the key comes from Figure 14 by trial.

## Next Actions

- Check the Appendix A.2 Type Metadata example (Figure 30) and the `vct#integrity` values against their documents.
