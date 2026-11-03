# Interop Checklist

- [ ] The signing input is stated unambiguously: confirm whether `sig` covers the JCS form of the object without the `signature` member, and that two implementations produce identical bytes (Sections 3, 5).
- [ ] A verifier handles the Abstract's COSE_Sign1 versus the JSON `signature` object in Section 3 consistently, and rejects the form it does not support instead of guessing.
- [ ] JCS and Deterministic CBOR (Section 3) versus JCS only (Section 5): check what a verifier does when it receives a CBOR-encoded CTA.
- [ ] The `Agent-Ctx-Isolation` header encoding (for example base64url of the JSON) is agreed between sender and receiver, and the `_meta.ctxIsolation` form carries the same object (Section 3).
- [ ] A call with no CTA, a malformed CTA, or an unknown `cta_version` is rejected for state-mutating effect classes. The draft does not say what happens for other classes.
- [ ] `kid` (a SHA-256 digest) resolves to a trusted Ed25519 key, and an unknown `kid` fails closed. Note that the key distribution is out of the draft.
- [ ] A CTA with `iat` or `exp` more than 60 seconds off the verifier's clock is rejected and an auditable rejection receipt is emitted (Section 5). Test the boundary at exactly 60 seconds and the example's 60-second `exp` minus `iat` window.
- [ ] A replayed CTA with the same `invocation_id` within its validity window is handled in a defined way. The draft does not require tracking, so record the actual behavior.
- [ ] `STATE_MUTATING` and `PRIVILEGED_ACTUATE` with `MIXED_TAINT` or `UNTRUSTED_INGESTED` return `ERR_TAINTED_CONTROL_PLANE` when no step-up receipt is attached (Section 4, rule 2).
- [ ] `TRUSTED_ONLY` with `STATE_MUTATING` is accepted, and the handling of a `TRUSTED_ONLY` claim paired with a non-empty `data_plane_merkle_root` is decided and documented.
- [ ] `QUARANTINED` (registered in Section 6, unused in Section 4) is rejected or handled in a documented way, and so is any `tool_effect_class` value not named in the draft.
- [ ] A step-up receipt that is expired, signed by the agent runtime itself, or bound to another `invocation_id` is rejected. The draft does not define the format, so the test must state the assumed format.
- [ ] `step_up_receipt_hash` matches the receipt carried in `Agent-Step-Up-Receipt`, and a mismatch fails closed (Sections 3, 6).
- [ ] The Merkle root is reproducible: two implementations given the same ordered chunks produce the same `data_plane_merkle_root`, with the leaf encoding and tree shape written down because Section 4, rule 3 leaves them open.
- [ ] `system_prompt_digest` and `parent_trace_ref` are checked or explicitly ignored by the verifier, since Section 4 states no rule for them.
- [ ] The taint level never moves back from `MIXED_TAINT` or `UNTRUSTED_INGESTED` to `TRUSTED_ONLY` inside one context session except through a defined reset boundary (Section 4, rule 1).
- [ ] The error `ERR_TAINTED_CONTROL_PLANE` is mapped to a concrete HTTP status and JSON-RPC error code in the test setup, since the draft gives none.
- [ ] The media type `application/agent-ctx-isolation+json` and the two header names are used exactly as written in Section 6.
