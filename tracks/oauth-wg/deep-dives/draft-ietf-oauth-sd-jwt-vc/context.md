# Context

## Trigger

The ARTART telechat review of draft-ietf-oauth-sd-jwt-vc-23 returned Ready on 3 November 2026, and the IESG ballot on -23 followed. The authors answered with -24 and -25 on 5 November and -26 on 6 November 2026. On Datatracker (checked 15 November 2026) the draft is Active at -26, its WG state is Submitted to IESG for Publication, its IESG state is IESG Evaluation::AD Followup with Deb Cooley as action holder, and no telechat date is set. The IANA review state is Version Changed - Review Needed and the IANA expert review state is Expert Reviews OK. The SECDIR telechat review of -26 returned Ready on 8 November 2026.

## Why This Matters

The draft defines the credential format that wallet and verifier implementations use for SD-JWT based credentials, and its HTTP retrieval and Type Metadata rules apply to every implementation that fetches metadata from `iss` or `vct` URLs. The ballot changed the text in two places that matter to implementers. -24 makes the draft update RFC 7800 so that `cnf` can be used without `sub` or `iss` in any JWT (Section 2.2.2.3.1), which cleared Mike Bishop's DISCUSS. -24 also says that the recipient's policy, not the credential, selects between JWT VC Issuer Metadata and `x5c`, and that inputs of the mechanism not in use do not identify the Issuer (Section 2.5). One DISCUSS remains, Éric Vyncke's, on the SHOULDs in Sections 2.2.2.2 and 2.4, which -25 reworded.

## Open Questions

- Will Éric Vyncke clear his DISCUSS on -25/-26, or ask for more on the status-check SHOULD in Section 2.4?
- Will Section 7.1 allow locally configured destinations, such as an allow-list, for closed deployments? -26 does not.
- Will a later revision cap the depth of `extends` chains or the total retrievals per credential, as Mahesh Jethanandani suggests? -26 does not.
- Will a later revision give metadata documents a dedicated media type, or say in Section 4.3 that `issuer` must equal `iss` regardless of redirects? -26 does neither.
