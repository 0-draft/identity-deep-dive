# Interop Checklist

- [ ] Read the merged diff of #368 and confirm which event signature mechanism is removed, and in which specification (SSF 1.1, CAEP 1.1 or both).
- [ ] Check that a 1.1 Receiver still handles events from a 1.0 Transmitter, including events that carry a signature.
- [ ] Check that a 1.0 Receiver does not reject events from a 1.1 Transmitter that omit what #368 removed.
- [ ] If #355 merges, test a Transmitter and Receiver that disagree on the SET signing algorithm, and check the failure is reported.
- [ ] Check how a Receiver treats a complex subject (#366) or an agent or workload subject (#362) it does not understand.
- [ ] Send JSON `null` for optional stream configuration properties (#369) and check that Transmitter and Receiver behave the same.
- [ ] Fetch Transmitter metadata and the JWK Set from a browser origin and check the CORS headers recommended in #367.
- [ ] Check that the CAEP Interoperability Profile Receiver requirements (#315) and the OAuth section (#325) match what the SSF text requires.
- [ ] Confirm which specification version string a Transmitter advertises, given the version section revision in #363.
