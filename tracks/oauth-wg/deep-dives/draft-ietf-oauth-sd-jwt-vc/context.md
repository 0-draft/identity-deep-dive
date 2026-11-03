# Context

## Trigger

The ART-ART telechat review of draft-ietf-oauth-sd-jwt-vc-23 returned Ready, so the draft is moving toward publication (`subject.json`). The Datatracker states in `subject.json` are Active, Expert Reviews OK, Version Changed - Review Needed, IESG Evaluation and Submitted to IESG for Publication.

## Why This Matters

The draft defines the credential format that wallet and verifier implementations use for SD-JWT based credentials, and its HTTP retrieval and Type Metadata rules apply to every implementation that fetches metadata from `iss` or `vct` URLs. The latest revision, -23, has no visible normative change (`diff.txt`), so what matters is the IESG evaluation around it: the mail shows a DISCUSS on the RFC 7800 override in Section 2.2.2.3 and a supporting No Objection with comments on Section 7.1 and Section 2.5 / 7.3. An earlier machine briefing called -23 a clean-up release, which matches the diff, but it did not mention the ballot positions.

## Open Questions

- How will the DISCUSS on Section 2.2.2.3 be resolved: an `Updates:` relationship to RFC 7800 or a rewording?
- Will Section 7.1 allow locally configured destinations for closed deployments?
- Will Section 2.5 and Section 7.3 be aligned on the choice between `x5c` and an HTTPS `iss`?
- Will a revision after -23 change the media types for metadata documents or the MUST keywords questioned in Section 5.5.1.2.1 and 7.6?
- Truncated ballot messages in `mail.txt` may hide further comments.
