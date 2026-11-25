# Context

## Trigger

Revision 04 of draft-ietf-oauth-first-party-apps was the top oauth-wg candidate without a deep dive. Its Datatracker states are "Active", "I-D Exists" and "WG Consensus: Waiting for Write-Up". WG Last Call on -03 ran from 25 June to 13 July 2026, -04 was posted on 1 July 2026 during it, and the WG state moved to "Waiting for Write-Up" on 15 July 2026.

## Why This Matters

The draft would give OAuth servers a standard endpoint for in-app sign-in by first-party native apps, as an alternative to the browser round trip (Section 1). Revision 04 makes HTTP 403 mandatory for `insufficient_authorization` and `redirect_to_web` (Section 5.2.2.1), which affects any server or SDK written against -03 (400 by default, 401 in the Appendix B.3 example). The draft pushes most interaction details to deployment-specific profiles (Section 1.2), so interoperability depends on profiles that the draft does not define beyond the Appendix B example.

## Open Questions

- No status code is given for `invalid_session`, so the 400 default of Section 5.2.2 applies (Section 5.2.2.1).
- No status code is set for `insufficient_authorization` at the token endpoint. The example uses 403, while [RFC6749] Section 5.2 defaults to 400 (Section 6.2).
- The IANA registration of `auth_session` lists only the token response as its usage location (Section 10.1).
- A broken `[IANA.JWT]` reference and a TODO about OAuth 2.1 remain in the text (Section 2.1, 11.1).
- How first-partyness is verified is out of scope (Section 9.1).
