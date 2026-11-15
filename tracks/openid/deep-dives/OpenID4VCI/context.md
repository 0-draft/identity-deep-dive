# Context

## Trigger

`subject.json` gives no reason for picking this repository (`ai_note` is empty). It was the top candidate on the `openid` track without a deep dive. This deep dive was checked against the drafts at commit `41c8c66` (10 November 2026) and the pull requests and issues it cites.

## Why This Matters

OpenID4VCI 1.0 is an OpenID Final Specification (approved 16 September 2025) and is the issuance half of the OpenID4VC family that HAIP 1.0 profiles. Work has moved to three places: errata for 1.0 (the metadata URL rule and Transaction Code guessing), 1.1 (Interactive Authorization on OAuth 2.0 for First-Party Applications, Credential Dataset parameters, `invalid_tx_code`), and a new Server to Server draft for Wallet Providers that run their own backend. An implementer has to know which of these texts a peer follows, because they differ on the wire.

## Open Questions

- Will the terminating `/` rule (#775) be published as 1.0 errata, and when?
- When will 1.1 reach an implementer's draft (#687)?
- How will deferred issuance in s2s (#816) settle, now that the identifier renames (#810) are merged?
- Will 1.0 errata reconcile Section 6.3 (`invalid_grant` for a wrong Transaction Code) with Section 13.6.3 (an error that says the Transaction Code is invalid)?
- How will the 1.1 identifier spelling (#811) and the per-format presentation binding (#812) be settled?
