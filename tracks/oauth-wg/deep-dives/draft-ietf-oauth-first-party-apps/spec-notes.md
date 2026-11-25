# Spec Notes

## References

Normative references listed in the draft (Section 11.1):

- [RFC6749], [RFC7636], [RFC8414], [RFC8259], [RFC9126], [RFC9449], [RFC9470], [RFC8628], [RFC8707], [RFC7591], [RFC7515], [RFC7519], [RFC2119], [RFC8174].
- [OpenID], [OpenID.Native-SSO], [IANA.oauth-parameters], [SHS], [USASCII].
- [I-D.ietf-oauth-cross-device-security] (-16).
- [IANA.JWT] appears as a broken reference.

Informative references listed in the draft (Section 11.2):

- [I-D.ietf-oauth-attestation-based-client-auth] (-09).
- [I-D.ietf-oauth-browser-based-apps] (-26).
- [RFC6750], [RFC8252], [RFC9207], [RFC9700].

## Key Changes

Revision 04 compared with 03:

- `insufficient_authorization` and `redirect_to_web` MUST use HTTP 403 (Section 5.2.2.1). The Appendix B.3 `otp_required` example moves from 401 to 403. The editor's WGLC reply (1 July 2026) says a 401 example lacked the `WWW-Authenticate` header that 401 requires.
- A `redirect_to_web` example with `request_uri` is added, with a SHOULD to follow [RFC9700] and [RFC9207] (Section 5.2.2.1.1).
- Clients SHOULD discard `auth_session` on logout (Section 5.3.1).
- `response_type=code` is added to the request example (Section 5.1).
- IANA pointers are corrected to Section 5.3.1 and Section 8 (Section 10).
- The [RFC7159] reference is dropped in favour of [RFC8259], and two RFCs are added as informative references.
- Appendix D describes the revision as editorial clarifications and updated response codes.

## Impact Analysis

- Upstream: builds on [RFC6749] and its token endpoint, reuses PKCE [RFC7636], pushed authorization requests [RFC9126], DPoP [RFC9449], step-up signalling [RFC9470] and server metadata [RFC8414]. It states that it does not change [RFC9470] (Section 3.3, 7).
- Downstream: authorization servers add the challenge endpoint and the `authorization_challenge_endpoint` metadata value (Section 8). Clients and SDKs implement `auth_session` handling. Deployments must define their own profile of requests and error codes (Section 1.2, Appendix B).
- Compatibility: implementations that follow -03 return 400 for both codes (the Section 5.2.2 default) or 401 for `insufficient_authorization` (the Appendix B.3 example), and both differ from -04. The draft is intended for first-party native apps and NOT RECOMMENDED for browser-based apps (Section 9.8). At the token endpoint, Section 6.2 sets no status code: its example uses 403 where [RFC6749] Section 5.2 defaults to 400.
