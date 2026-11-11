# Spec Notes

## References

Normative references listed in the draft (Section 13.1):

- [OpenID.RPMetadataChoices] OpenID Connect Relying Party Metadata Choices 1.0 (new in -03)
- [RFC2119] and [RFC8174] (BCP 14)
- [RFC3986] URI generic syntax
- [RFC6749] OAuth 2.0
- [RFC6819] OAuth 2.0 threat model
- [RFC6890] special-purpose IP address registries
- [RFC7523] JWT profile for OAuth 2.0 client authentication (informative in -02, normative in -03)
- [RFC7591] Dynamic Client Registration
- [RFC8259] JSON
- [RFC8414] Authorization Server Metadata
- [RFC8725] JWT best current practices (new in -03)
- [RFC9110] HTTP semantics (new in -03)
- [RFC9207] authorization server issuer identification (new in -03)
- [RFC9700] OAuth 2.0 security best current practice

Informative references (Section 13.2):

- [I-D.draft-ietf-oauth-attestation-based-client-auth] (-12, was -09 in -02)
- [I-D.draft-ietf-oauth-rfc7523bis] (new, -11)
- [I-D.draft-ietf-oauth-spiffe-client-auth] (-03, was -02 in -02)
- [IndieAuth]
- [OpenID] Connect Core 1.0
- [OpenID.Federation] (1.1, was 1.0 in -02)
- [OWASP.SSRF] (new)
- [RFC9111] HTTP caching
- [Solid-OIDC]

## Key Changes

- Section 3: the path `/` is prohibited, clients SHOULD normalize the URL per Sections 6.2.2 and 6.2.3 of [RFC3986], and the server MUST NOT normalize.
- Section 4.1: restrictions now cover token_endpoint_auth_methods_supported and software_statement content, and jwks and jwks_uri MUST NOT both be present.
- Sections 4.4 and 4.5: functional versus informative URIs, and a ban on deriving document contents from untrusted external input.
- Section 5 (moved from Security Considerations, -02 Section 8.2, and expanded): authentication defaults to none, token_endpoint_auth_method is NOT RECOMMENDED, the RFC7591 default is not applied, and the server rejects with invalid_client when it supports none of the declared methods.
- Section 6: grant_types and response_types intersection with invalid_client on empty, plus an Accept header recommendation.
- Section 6.1: transient and terminal failure classes, no redirect of the user agent to the client, and invalid_client or HTTP 503 at the token and PAR endpoints.
- Section 6.2: the -02 MAY for server-defined cache bounds becomes a SHOULD to enforce a maximum effective cache duration and a SHOULD to enforce a minimum when none is indicated, Expires need not be honoured, caching extends to jwks_uri and logo_uri data, and rate limiting is allowed (MAY). Errors and malformed documents are still never cached.
- Section 7 (new): the authorization response MUST include iss.
- Section 10: new subsections on URL confusion (10.1), Accept header (10.7.1), client presentation (10.10) and resource-scoped persisted state (10.12). Logo prefetching and re-serving went from SHOULD to MUST, with a MUST to validate the image (10.9), and Section 10.7 adds a SHOULD to follow the OWASP SSRF cheat sheet.
- Section 11.1: adds a warning about varying documents by requester.
- Section 12.1: the specification document reference is now Section 8 of -03.

## Impact Analysis

- Upstream: depends on OAuth 2.0 [RFC6749], Dynamic Client Registration metadata [RFC7591], Authorization Server Metadata [RFC8414], the security best current practice [RFC9700], issuer identification [RFC9207], and the OpenID metadata choices specification for token_endpoint_auth_methods_supported. The JWT `typ` recommendation points to a Work in Progress draft (rfc7523bis), which is not final.
- Downstream: authorization server implementations that accept URL client_ids, client libraries and publishers of metadata documents, and any CIMD Service operators. Future specifications may place extra restrictions on document contents (Section 4). The only IANA action is the client_id_metadata_document_supported authorization server metadata name (Section 12.1).
- Compatibility: section numbers from Section 5 on differ from -02. The default authentication method and the logo and iss requirements change observable behaviour. token_endpoint_auth_method remains readable as a fallback. The draft is a Work in Progress and may change again.
