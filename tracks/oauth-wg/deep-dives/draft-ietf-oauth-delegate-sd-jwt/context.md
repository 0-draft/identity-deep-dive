# Context

## Trigger

`subject.json` gives this reason: "PR #15 restructures where security claims live in the KB-SD-JWT and defines their delegation semantics." That pull request is not in the staged material and was not checked. The subject is draft-ietf-oauth-delegate-sd-jwt revision 00, in the oauth-wg track, with datatracker states Active, I-D Exists and WG Document.

## Why This Matters

The draft extends SD-JWT (RFC 9901) so that a Holder can delegate presentation to another party, with AI agents as the named example (Abstract, Section 1). It changes the KB-JWT into something that can itself be an SD-JWT, so any SD-JWT verifier or wallet that wants to support delegation has to handle chained tokens, new `typ` values and the `issuer_jwt_hash` claim (Sections 5.1.4, 6). The security rules for the chain sit mostly in Section 8.1 and Section 6.

## Open Questions

- How the `delegate_payload` array, the Delegate Payload object and the Disclosure digests fit together is not shown by an example (Sections 5.1.3, 5.1.4).
- Whether a delegation can only narrow the earlier grant is not stated (Section 8.2).
- The privacy section only points to RFC 9901 (Section 9).
- The content of PR #15 is not in the material, so how it relates to -00 is unknown.
