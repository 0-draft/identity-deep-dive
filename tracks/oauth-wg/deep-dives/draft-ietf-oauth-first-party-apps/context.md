# Context

## Trigger

`subject.json` names revision 04 of draft-ietf-oauth-first-party-apps in the oauth-wg track. Its Datatracker states are "Active", "I-D Exists" and "WG Consensus: Waiting for Write-Up". The `ai_note` field is empty, so no further reason for picking it is recorded.

## Why This Matters

The draft would give OAuth servers a standard endpoint for in-app sign-in by first-party native apps, as an alternative to the browser round trip (Section 1). Revision 04 makes HTTP 403 mandatory for `insufficient_authorization` and `redirect_to_web` (Section 5.2.2.1), which affects any server or SDK written against earlier examples. The draft pushes most interaction details to deployment-specific profiles (Section 1.2), so interoperability depends on profiles that are not yet defined in the material.

## Open Questions

- The status code for `invalid_session` is not stated (Section 5.2.2.1).
- HTTP 403 at the token endpoint sits next to a citation of [RFC6749] Section 5.2 (Section 6.2).
- The IANA registration of `auth_session` lists only the token response as its usage location (Section 10.1).
- A broken `[IANA.JWT]` reference and a TODO about OAuth 2.1 remain in the text (Section 2.1, 11.1).
- How first-partyness is verified is out of scope (Section 9.1).
