# Spec Notes

## References

The staged material is the README, which does not list normative or informative references. It names the following documents the repository holds.

- Shared Signals Framework 1.1 (draft) and 1.0 (final)
- CAEP 1.1 (draft) and 1.0 (final)
- CAEP Interoperability Profile 1.0 (draft)
- RISC 1.0 (final)

The build tools named are `xml2rfc` and `kramdown-rfc`.

## Key Changes

- #310 (merged): creates the 1.1 draft documents from 1.0 and retains 1.0.
- #368 (merged): "Drop event signatures". The diff is not staged, so the scope is unverified.
- #343 (merged): creates Draft-01 of the CAEP Interoperability Profile for OIDF Review.
- #349 (merged): adds a risk level change use case to the CAEP Interoperability Profile.
- #315 (merged): adds Receiver requirements to the CAEP Interoperability Profile.
- Open proposals: #366 complex subjects, #355 SET signing algorithm negotiation, #369 JSON null handling, #367 CORS recommendation, #362 agent and workload as subject or principal, #363 specification version section in the CAEP Interoperability Profile, #329 device management status in device compliance change.

## Impact Analysis

- Upstream: the material names no dependencies beyond the build tools. Dependence on the SET format and JWT/JWS specifications is likely but not stated in the material.
- Downstream: Transmitter and Receiver implementers of SSF and CAEP, and deployers following the CAEP Interoperability Profile.
- Compatibility: 1.0 documents are retained and 1.1 is a separate folder. Whether 1.1 is compatible with 1.0, and what #368 means for 1.0 Receivers, is not shown.
