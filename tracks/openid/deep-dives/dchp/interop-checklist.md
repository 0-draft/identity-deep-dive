# Interop Checklist

- [ ] Record the commit of `openid/dchp` you implement (for example `4ddd238`). The README says the Editor's Copy is not an approved Working Group Draft, and every core clause still lacks working group consensus.
- [ ] Encode `CredentialQuery.credential_types` (key 2) as an array of text strings (pull request #61). Check that a query with n types is processed as n queries, and that every combination referencing it is expanded the same way.
- [ ] Use `dc+sd-jwt`, not `vc+sd-jwt`, as the SD-JWT VC `credential_format` (pull request #57). Match `credential_types` against the mdoc `docType` or the SD-JWT VC `vct` as a case-sensitive string comparison.
- [ ] Take `ChannelBinding` integer keys from one agreed source. On `main` the prose and the CDDL disagree: `dc_api_origin` is key 8 in the prose and key 7 in the CDDL, and the BLE fields differ. Open pull request #76 aligns them to the prose numbering.
- [ ] Encode both transaction transcripts with deterministic CBOR (RFC 8949 Section 4.2; open pull request #64 pins Section 4.2.1), and check that verifier and wallet compute the same SHA-256 of the `RequestPayload` bytes.
- [ ] Agree with your peer which transcript is the HPKE info for response encryption. The transcript list and CDDL comment say `ReaderTransactionTranscript`, and the "Use in Protocol Operations" table says `WalletTransactionTranscript`.
- [ ] Without session-layer encryption (Digital Credentials API, scheme-based invocation), always encrypt the response. Check that each `encrypted` entry is a `COSE_Encrypt` that decrypts to an `Envelope`, and that `encryption_ref` selects the right entry of `additional_encryption_contexts`.
- [ ] Verify `reader_auth` as a `COSE_Sign` with a detached payload of the `RequestPayload` bytes and the `ReaderTransactionTranscript`. How the reader key is conveyed is open: pull request #65 proposes an `x5chain` in the protected header.
- [ ] Check `issuer_identifiers.x509_ref` against the `keyIdentifier` of the Authority Key Identifier (RFC 5280) of each certificate in the mdoc `IssuerAuth` `x5chain` or the SD-JWT VC `x5c` header.
- [ ] Return a non-key-bound mdoc, or an SD-JWT VC without a KB-JWT, only when `support_no_cryptographic_binding` is `true`. The text states only this wallet rule, so decide how your verifier treats such a credential when it did not set the flag.
- [ ] Do not interoperate on the SD-JWT VC binding yet. The KB-JWT `nonce` is the SHA-256 of the `WalletTransactionTranscript`, but its string encoding and the `aud` value are open (issue #10). The SD-JWT VC `path` is open as well (issue #52).
- [ ] If pull request #77 merges, move response parsing from a `CredentialRef`-keyed map to an array with `query_refs`, and test one credential answering two queries and two credentials answering one query with `allow_multiple`.
- [ ] Do not rely on Security Considerations text: none exists on `main`, and pull request #85 adds only a placeholder.
