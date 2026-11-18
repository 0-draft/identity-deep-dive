# Context

## Trigger

[PR #15](https://github.com/oauth-wg/oauth-delegate-sd-jwt/pull/15) in the draft's repository, "Move security claims to base KB-SD-JWT payload and define claim semantics", opened on 2026-11-10 and still open on 2026-11-18. It fixes issues #3 and #10, moves `cnf`, `exp`, `nbf` and the other security claims out of `delegate_payload` into the base KB-SD-JWT payload, defines what each claim means at each step of the chain, and updates the Verification section. The subject is draft-ietf-oauth-delegate-sd-jwt revision 00, in the oauth-wg track, with datatracker states Active, I-D Exists and WG Document.

## Why This Matters

The draft extends SD-JWT (RFC 9901) so that a Holder can delegate presentation to another party, with AI agents as the named example (Abstract, Section 1). It changes the KB-JWT into something that can itself be an SD-JWT, so any SD-JWT verifier or wallet that wants to support delegation has to handle chained tokens, new `typ` values and the `issuer_jwt_hash` claim (Sections 5.1.4, 6). The security rules for the chain sit mostly in Section 8.1 and Section 6.

## Open Questions

- How the `delegate_payload` array, the Delegate Payload object and the Disclosure digests fit together is not shown by an example (Sections 5.1.3, 5.1.4). PR #14 proposes a worked example.
- Whether a delegation can only narrow the earlier grant is not stated in -00 (Section 8.2). Issue #8 asks for it, and PR #15 would require it only for `exp` and `nbf`.
- The privacy section only points to RFC 9901 Section 10 (Section 9).
- PR #15 is not merged, so which parts of -00 it will change is not settled.
