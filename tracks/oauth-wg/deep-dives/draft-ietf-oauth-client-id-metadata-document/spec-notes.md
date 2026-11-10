# Spec Notes

## References

Normative references listed in the draft (Section 13.1):

- [OpenID.RPMetadataChoices] OpenID Connect Relying Party Metadata Choices 1.0 (new in -03)
- [RFC2119] and [RFC8174] (BCP 14)
- [RFC3986] URI generic syntax
- [RFC6749] OAuth 2.0
- [RFC6819] OAuth 2.0 threat model
- [RFC6890] special-purpose IP address registries
- [RFC7523] JWT profile for OAuth 2.0 client authentication (moved from informative in -02, new as normative in -03)
- [RFC7591] Dynamic Client Registration
- [RFC8259] JSON
- [RFC8414] Authorization Server Metadata
- [RFC8725] JWT best current practices (new in -03)
- [RFC9110] HTTP semantics (new in -03)
- [RFC9207] authorization server issuer identification (new in -03)
- [RFC9700] OAuth 2.0 security best current practice

Informative references (Section 13.2):

- [I-D.draft-ietf-oauth-attestation-based-client-auth] (now -12)
- [I-D.draft-ietf-oauth-rfc7523bis] (new, -11)
- [I-D.draft-ietf-oauth-spiffe-client-auth] (now -03)
- [IndieAuth]
- [OpenID] Connect Core 1.0
- [OpenID.Federation] (now 1.1)
- [OWASP.SSRF] (new)
- [RFC9111] HTTP caching
- [Solid-OIDC]

## Key Changes

- Section 3: the path `/` is prohibited, clients SHOULD normalize the URL per Sections 6.2.2 and 6.2.3 of [RFC3986], and the server MUST NOT normalize.
- Section 4.1: restrictions now cover token_endpoint_auth_methods_supported and software_statement content, and jwks with jwks_uri must not both be present.
- Sections 4.4 and 4.5: functional versus informative URIs, and a ban on deriving document contents from untrusted external input.
- Section 5 (new): authentication defaults to none, token_endpoint_auth_method is NOT RECOMMENDED, the RFC7591 default is not applied, and the server rejects with invalid_client when it supports none of the declared methods.
- Section 6: grant_types and response_types intersection with invalid_client on empty, plus an Accept header recommendation.
- Section 6.1: transient and terminal failure classes, no redirect of the user agent to the client, and invalid_client or HTTP 503 at the token and PAR endpoints.
- Section 6.2: maximum and minimum effective cache duration, no caching of errors or malformed documents, and optional rate limiting.
- Section 7 (new): the authorization response MUST include iss.
- Section 10: new subsections on URL confusion (10.1), Accept header (10.7.1), client presentation (10.10) and resource-scoped persisted state (10.12). Logo prefetching is now MUST (10.9).
- Section 11.1: adds a warning about varying documents by requester.
- Section 12.1: the specification document reference is now Section 8 of -03.

## Impact Analysis

- Upstream: depends on OAuth 2.0 [RFC6749], Dynamic Client Registration metadata [RFC7591], Authorization Server Metadata [RFC8414], the security best current practice [RFC9700], issuer identification [RFC9207], and the OpenID metadata choices specification for token_endpoint_auth_methods_supported. The JWT `typ` recommendation points to a Work in Progress draft (rfc7523bis), which is not final.
- Downstream: authorization server implementations that accept URL client_ids, client libraries and publishers of metadata documents, and any CIMD Service operators. Future specifications may place extra restrictions on document contents (Section 4). The only IANA action is the client_id_metadata_document_supported authorization server metadata name (Section 12.1).
- Compatibility: section numbers differ from -02. The default authentication method and the logo and iss requirements change observable behaviour. token_endpoint_auth_method remains readable as a fallback. The draft is a Work in Progress and may change again.
