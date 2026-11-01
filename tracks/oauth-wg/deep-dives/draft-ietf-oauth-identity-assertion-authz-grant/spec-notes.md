# Spec Notes

## References

Normative references listed in Section 12.1:

- Work in progress: draft-ietf-oauth-identity-chaining-17 (OAuth Identity and Authorization Chaining Across Domains) and draft-parecki-oauth-jwt-dpop-grant-02 (OAuth 2.0 JWT Authorization Grant with DPoP Binding).
- OAuth core and assertion framework: RFC 6749, RFC 7521, RFC 7523, RFC 8693 (Token Exchange), RFC 8707 (Resource Indicators), RFC 8414 (Authorization Server Metadata), RFC 9728 (Protected Resource Metadata, moved to normative in -05), RFC 7591 (Dynamic Client Registration).
- Tokens and keys: RFC 7518, RFC 7519, RFC 7638, RFC 7800, RFC 8725 (JWT BCP), RFC 9449 (DPoP), RFC 8705 (mutual TLS), RFC 9396 (Rich Authorization Requests), RFC 9493 (Subject Identifiers for Security Event Tokens).
- Other: RFC 2046, RFC 2119, RFC 3986, RFC 6838, RFC 8174, OASIS SAML Core 2.0, OpenID Connect Core 1.0, OpenID Connect Discovery 1.0, OpenID Connect Enterprise Extensions 1.0 draft 01, and the IANA registries for JWT, Media Types and OAuth Parameters.

Informative references listed in Section 12.2:

- draft-ietf-oauth-client-id-metadata-document-02, RFC 9068 (JWT Profile for OAuth 2.0 Access Tokens) and RFC 9470 (Step Up Authentication Challenge).

## Key Changes

Changed in -06 (diff: <https://author-tools.ietf.org/iddiff?url1=draft-ietf-oauth-identity-assertion-authz-grant-05&url2=draft-ietf-oauth-identity-assertion-authz-grant-06>):

- IdP error for a subject token that fails validation changed from `invalid_grant` to `invalid_request`, citing RFC 8693 Section 2.2.2. A Client that gets `invalid_request` for a request that previously succeeded can get a new subject token and retry (Section 4.3.4.3).
- New explanation that `access_denied` is used instead of `invalid_target` when the Client or End-User is not authorized for the target, so the Client can distinguish a forbidden target from an unrecognized one (Section 4.3.4.3).
- Document History only: entries were added under -05 for changes whose text was already in the -05 body (listed below).
- Dates and version strings moved to 31 October 2026 and an expiry of 4 May 2027.

Introduced in -05 (absent from the -04 text, present in -05):

- Client authentication required at the IdP, with `invalid_client` (Section 4.3.3).
- A single `audience` value, `invalid_target` handling, resource comparison by Simple String Comparison, and `resource` RECOMMENDED in the Token Exchange request (Section 4.3.3).
- mTLS certificate binding alongside DPoP (Section 9.11.2).
- `id_jag_signing_alg_values_supported` metadata and RS256 mandatory to implement (Sections 3 and 7.1).
- Storage guidance for subject tokens (Section 9.2).
- Privacy Considerations (Section 10).

Already in -04 and extended in -05: the `jwt-dpop` grant type for DPoP-bound ID-JAGs, the `saml-nameid` Subject Identifier Format with more NameID rules in -05, and the email and calendaring example, which -05 ties to the Client ID Metadata Document.

## Impact Analysis

- Upstream: the profile sits on RFC 8693 (Token Exchange), RFC 7523 (JWT bearer grant), OpenID Connect or SAML for the SSO assertion, RFC 8414 and RFC 9728 for discovery, RFC 9449 and RFC 8705 for sender constraining, and the Identity Chaining draft (cited at -17), which defines `identity_chaining_requested_token_types_supported`. Changes in those documents, particularly the two Work in Progress drafts, can change this one.
- Downstream: IdPs must implement the Token Exchange profile with mandatory client authentication, subject token typing, audience and resource policy, and the required error codes. Resource Authorization Servers must implement ID-JAG validation, tenant handling, resource and scope policy, and an optional sender-constraining path. Clients must register at both servers (or use Client ID Metadata Documents), validate discovery metadata, and manage subject token storage. IANA registrations requested: media type `oauth-id-jag+jwt`, token type URI `urn:ietf:params:oauth:token-type:id-jag`, grant profile URI `urn:ietf:params:oauth:grant-profile:id-jag`, metadata names `authorization_grant_profiles_supported` and `id_jag_signing_alg_values_supported`, JWT claims `resource` and `aud_tenant`, and the Subject Identifier Format `saml-nameid`.
- Compatibility: an IdP that returns `invalid_grant` for a bad subject token, accepts unauthenticated Token Exchange requests, or accepts several audiences is not conformant with -06. A Resource Authorization Server must reject a request that has neither client authentication nor a sender-constrained ID-JAG, and must reject an ID-JAG whose `cnf` method it does not support. The draft is still a working group draft, so wire details can change before publication.
