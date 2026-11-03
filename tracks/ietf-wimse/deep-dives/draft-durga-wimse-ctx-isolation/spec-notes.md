# Spec Notes

## References

Normative references listed in Section 7:

- RFC 2119, Key words for use in RFCs to Indicate Requirement Levels (BCP 14).
- RFC 8174, Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (BCP 14).
- RFC 8785, JSON Canonicalization Scheme (JCS).
- RFC 8032, Edwards-Curve Digital Signature Algorithm (EdDSA).

Informative references: the draft has no informative reference section.

Cited in the text but not listed in Section 7:

- RFC 8693, OAuth 2.0 Token Exchange (Section 1).
- RFC 8949, Concise Binary Object Representation (CBOR), for its deterministic encoding (Section 3).
- OAuth 2.1, GNAP and "WIMSE Wit/Wpt tokens" (Abstract), and WIMSE Workload Identity Tokens (Section 1), named without a reference.
- COSE_Sign1 (Abstract), named without a reference.
- draft-durga-agenttrust-trace-verification-00, described as the "foundational execution-trace verification architecture" this draft complements (Section 1).

## Key Changes

This is revision 00, so there is no earlier revision and no `diff.txt`. What it introduces:

- A Context Taint Attestation object with `cta_version`, `invocation_id`, `parent_trace_ref`, `system_prompt_digest`, `data_plane_merkle_root`, `taint_lattice_level`, `tool_effect_class`, `step_up_receipt_hash`, `iat`, `exp` and a `signature` member with `alg`, `kid` and `sig` (Section 3).
- Carriage in an `Agent-Ctx-Isolation` header or `_meta.ctxIsolation` in JSON-RPC/MCP (Section 3).
- Three invariants: `TAINT_LATTICE_MONOTONICITY`, `CONFUSED_DEPUTY_FAIL_CLOSED` with error `ERR_TAINTED_CONTROL_PLANE`, and `CONTEXT_MERKLE_BINDING` (Section 4).
- Fail-closed handling of clock skew over 60 seconds, digest mismatch and missing binding, with an auditable rejection receipt (Section 5).
- IANA requests: media type `application/agent-ctx-isolation+json`, a registry of taint levels (`TRUSTED_ONLY`, `MIXED_TAINT`, `UNTRUSTED_INGESTED`, `QUARANTINED`), and header fields `Agent-Ctx-Isolation` and `Agent-Step-Up-Receipt` (Section 6).

Gaps visible in the text: the Abstract says COSE_Sign1 but Section 3 shows a JSON signature object; the Merkle tree construction, step-up receipt format and header encoding are not defined; the example does not make clear what is signed. The example values are placeholders: the digests are SHA-256 of short strings (`data_plane_merkle_root` of empty input, `parent_trace_ref` of `test`, `kid` of `test1`), and `exp` is `iat` plus 60 seconds.

## Impact Analysis

- Upstream: Depends on JCS (RFC 8785) and EdDSA (RFC 8032) for canonicalization and signing, and on the agent runtime to track the taint level. It positions itself against RFC 8693 and WIMSE tokens but defines no binding to them. The companion draft draft-durga-agenttrust-trace-verification-00 is named in Section 1 but not listed as a reference. Neither draft says that `parent_trace_ref` points into it; the companion's own record field is `parent_record_hash`.
- Downstream: Every MCP or A2A tool server or gateway that wants to enforce Section 4 would have to parse and verify the header, manage signer keys, and implement a step-up approval path. New IANA registrations would be needed for the media type, the taint registry and two headers.
- Compatibility: Mandatory on every control-plane tool invocation (Section 3), with no negotiation or fallback described. Deterministic CBOR is allowed in Section 3 while Section 5 requires JCS, so implementations could diverge. The mail refers to `ctx_isolation_witness` and `policy_manifest_sha256`, which are not in revision 00 of either draft, so later revisions may change the structure.
