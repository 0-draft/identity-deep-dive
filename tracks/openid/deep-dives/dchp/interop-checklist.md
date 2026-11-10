# Interop Checklist

- [ ] Confirm which revision of the Editor's Copy an implementation targets, since credential_type became an array (pull request #61) and the README says the copy is not an approved Working Group Draft.
- [ ] Test that a request with a single credential type and a request with several credential types are both parsed correctly after the array change.
- [ ] Check that element names use the casing of the current Editor's Copy, for example CredentialQuery and scenario_sets (pull requests #83, #82, #73, #59), and that a parser rejects or handles the old casing as intended.
- [ ] Verify that ISO mdoc and IETF SD-JWT VC handling follows the per-format annexes (pull request #57) and not older core text.
- [ ] Compare the CDDL with the prose for every message you implement, because pull request #76 reports inconsistencies.
- [ ] Test responses that return several credentials for one query and several queries for one credential, if pull request #77 is merged.
- [ ] Check that any CBOR you sign or hash uses the deterministic encoding the specification requires, if pull request #64 is merged.
- [ ] Check reader authentication with an X.509 certificate chain, including the header placement, if pull request #65 is merged.
- [ ] Do not rely on security considerations text yet, since pull request #85 adds only a placeholder.
