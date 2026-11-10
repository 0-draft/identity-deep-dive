# Spec Notes

## References

The staged material does not include the specification text, so its normative and informative reference lists are not available. The README links to these documents:

- ISO/IEC 18013-5: <https://www.iso.org/standard/69084.html>
- OpenID for Verifiable Presentations: <https://openid.net/specs/openid-4-verifiable-presentations-1_0.html>
- The Editor's Copy: <https://openid.github.io/dchp/digital-credentials-harmonized-presentation-editors-copy.html>

The earlier briefing in `insights.md` mentions RFC 7515 being added as a normative reference and the RFC 5280 name for the authority key identifier. These come from commit titles only and are not confirmed.

## Key Changes

- Merged: #61 makes credential_type an array.
- Merged: #57 moves credential format specific details into per-format annexes.
- Merged: #29 adds the initial proposal, and #11, #15 and #7 add build and housekeeping files.
- Open: #64 deterministic CBOR encoding, #77 multiple credentials per query and multiple queries per credential in the Credential Response, #74 abbreviations for M, O, C, #76 CDDL and prose inconsistencies, #81 verifier terminology, #65 reader authentication X.509 certificate header, #83 casing of elements, #85 Security Considerations placeholder and Notices appendix.
- Closed without merge: #84 (an earlier version of #85), #82 and #73 (casing of CredentialQuery), #59 (scenario_sets casing).

## Impact Analysis

- Upstream: ISO/IEC 18013-5 Device Request / Device Response and OpenID for Verifiable Presentations Authorization Request / Authorization Response are the protocols being harmonized. The format annexes depend on ISO mdoc and IETF SD-JWT VC.
- Downstream: Wallets and verifiers that need one request protocol for in-person and online presentation. The material names no concrete adopters.
- Compatibility: Making credential_type an array and renaming fields break implementations of earlier editor's copies. Casing changes may affect wire names. The README states that the Editor's Copy is not an approved Working Group Draft.
