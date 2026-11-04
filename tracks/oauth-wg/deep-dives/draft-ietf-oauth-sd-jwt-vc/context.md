# Context

## Trigger

The ARTART telechat review of draft-ietf-oauth-sd-jwt-vc-23 returned Ready on 3 November 2026, so the draft is moving toward publication (`subject.json`). On Datatracker (4 November 2026) the draft is Active, its WG state is Submitted to IESG for Publication, its IESG state is IESG Evaluation and it is on the 5 November 2026 telechat agenda. The IANA review state is Version Changed - Review Needed, which Datatracker set when -23 was posted on 31 October 2026 (it was IANA OK - Actions Needed for -22), and the IANA expert review state is Expert Reviews OK.

## Why This Matters

The draft defines the credential format that wallet and verifier implementations use for SD-JWT based credentials, and its HTTP retrieval and Type Metadata rules apply to every implementation that fetches metadata from `iss` or `vct` URLs. The latest revision, -23, has no visible normative change (`diff.txt`), so what matters is the IESG evaluation around it: Mike Bishop holds a DISCUSS on the RFC 7800 override in Section 2.2.2.3, and Mahesh Jethanandani and Roman Danyliw support it in No Objection comments. Mahesh Jethanandani also raises Section 7.1 and Sections 2.5 and 7.3, and Roman Danyliw also supports the point on Sections 2.5 and 7.3. An earlier machine briefing called -23 a clean-up release, which matches the diff, but it did not mention the ballot positions.

## Open Questions

- How will the DISCUSS on Section 2.2.2.3 be resolved: an `Updates:` relationship to RFC 7800 or a rewording?
- Will Section 7.1 allow locally configured destinations for closed deployments?
- Will Section 2.5 and Section 7.3 be aligned on the choice between `x5c` and an HTTPS `iss`?
- Will a revision after -23 change the media types for metadata documents or the MUST keywords questioned in Section 5.5.1.2.1 and 7.6?
- Will a later revision cap the depth of `extends` chains or the total retrievals per credential, as Mahesh Jethanandani suggests?
