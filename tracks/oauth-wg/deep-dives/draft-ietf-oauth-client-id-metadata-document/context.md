# Context

## Trigger

The pick note in `subject.json` says 11 issues were closed and a new response_types issue (#131) was opened this week, with PRs adding a Client Authentication section. The staged material does not include those issues or PRs. The draft is at revision 03 (2 November 2026), and Datatracker lists it as Active, I-D Exists and WG Document in the oauth-wg track.

## Why This Matters

The draft lets a client use an HTTPS URL as its client_id, with the authorization server fetching the metadata from it (Sections 3 and 6). Revision 03 adds or tightens a number of normative rules, such as client authentication defaults (Section 5), failure handling (Section 6.1), the mandatory iss parameter (Section 7) and logo re-serving, which was a SHOULD in -02 and is now a MUST (Section 10.9). Implementers of authorization servers and clients that rely on URL client_ids are directly affected, and every section from Section 5 on has a new number.

## Open Questions

- Does the jwks or jwks_uri requirement in Section 5 apply only to private_key_jwt, or to every document that offers it among several methods?
- What does the server do when grant_types or response_types are absent from the document (Section 6)? The draft does not say.
- How should invalid_client be mapped at the authorization endpoint, given the editorial note about OAuth 2.1 issue 266 (Section 5)?
- Will the working group take up the mail-thread proposals: a pre-fetch validation step, MUST NOT for query components, and a registration-types list in server metadata (Sections 3, 6, 8 and 9.2)?
