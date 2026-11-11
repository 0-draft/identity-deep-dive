# Context

## Trigger

The pick came from activity in the draft's GitHub repository. On 2 November 2026, the day -03 was posted, 11 issues were closed and PR #99 "Add Client Authentication section" was merged. On 8 November, issue #131 was opened about the response_types intersection rule in Section 6. The draft is at revision 03 (2 November 2026), and Datatracker lists it as Active, I-D Exists and WG Document in the oauth-wg track.

## Why This Matters

The draft lets a client use an HTTPS URL as its client_id, with the authorization server fetching the metadata from it (Sections 3 and 6). Revision 03 adds or tightens a number of normative rules, such as client authentication defaults (Section 5), failure handling (Section 6.1), the mandatory iss parameter (Section 7) and logo re-serving, which was a SHOULD in -02 and is now a MUST (Section 10.9). Implementers of authorization servers and clients that rely on URL client_ids are directly affected, and every section from Section 5 on has a new number.

## Open Questions

- Does the jwks or jwks_uri requirement in Section 5 apply only when private_key_jwt is actually used, or to every document that offers it among several methods?
- What does the server do when grant_types or response_types are absent from the document (Section 6)? The draft does not say, nor whether the RFC 7591 defaults (`authorization_code` and `code`) apply. Issue #131 asks for the rule to be revisited, including this case.
- How should invalid_client be mapped at the authorization endpoint, given the editorial note about OAuth 2.1 issue 266 (Section 5)?
- Will the working group take up the proposals one participant made on the mailing list: a pre-fetch validation step, MUST NOT for query components, and a registration-types list in server metadata (Sections 3, 6, 8 and 9.2)?
