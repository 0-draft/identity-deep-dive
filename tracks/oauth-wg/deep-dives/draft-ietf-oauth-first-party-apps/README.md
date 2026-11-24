# Deep Dive: draft-ietf-oauth-first-party-apps

> In one line: OAuth 2.0 for First-Party Applications (-04) adds an Authorization Challenge Endpoint so a first-party native app can run the sign-in dialogue itself, receive an authorization code, and redeem it at the normal token endpoint, with a redirect to the browser only as a fallback.

## What this is

Redirect-based OAuth sends the user from a native app to a browser and back, which the draft says can disrupt the user journey and prevent task completion (Section 1). This draft adds a new HTTP endpoint at the authorization server, the Authorization Challenge Endpoint (Section 4.1). The client POSTs what it has collected from the user, and the server answers with either an authorization code or an error that tells the client to continue. The draft deliberately does not define the prompts, challenges or step sequences, which are left to each deployment (Section 1.2), and says the specification is meant to be profiled. It is limited to first-party applications, meaning apps controlled by the same entity as the authorization server and understood by users as the same entity (Section 1.1, 9.1). The draft also extends the token response and the resource server error handling so the server can ask for re-authentication (Section 6, 7).

## How it works

```mermaid
sequenceDiagram
    participant U as User
    participant C as First-party client
    participant CE as Authorization Challenge Endpoint
    participant T as Token Endpoint
    participant B as Browser
    C->>U: Show sign-in or collect username
    U-->>C: Information
    C->>CE: POST authorization challenge request
    CE-->>C: insufficient_authorization error with auth_session
    C->>U: Ask for the next factor
    U-->>C: Code or signed challenge
    C->>CE: POST request with auth_session
    CE-->>C: authorization_code
    C->>T: Token request with the code
    T-->>C: Access token, optional refresh token and auth_session
    Note over CE,B: If the server answers redirect_to_web, the client starts a browser flow, optionally using a request_uri
```

1. The client collects initial information such as a username and POSTs it to the Authorization Challenge Endpoint with `response_type=code`, plus `client_id` unless the server can identify the client otherwise (Section 5.1).
2. If the information is not enough, the server must return an error. `insufficient_authorization` means the client should take more steps, and the response must use HTTP 403 (Section 5.2.2.1). It may carry an `auth_session` and AS-defined custom values (Section 5.2.2).
3. The client repeats requests, always including the `auth_session` it holds. Intermediate requests may be in a different format or go to proprietary endpoints (Section 5.3).
4. When satisfied, the server returns HTTP 200 with `authorization_code` (Section 5.2.1).
5. The client redeems the code at the token endpoint. No `redirect_uri` is sent because none was in the authorization request (Section 6).
6. If the server wants direct interaction, it returns `redirect_to_web` with HTTP 403, optionally with a `request_uri` from a pushed authorization request. Without one, the client starts a normal authorization code flow with PKCE (Section 5.2.2.1.1).
7. Later, the token endpoint can answer even a valid refresh token with `insufficient_authorization` (Section 6.2), and a resource server can send an [RFC9470] step-up error that the client answers at the challenge endpoint (Section 7).

## Use cases

- A bank or other service signs users into its own mobile app with a passkey without leaving the app (Appendix A.1).
- A first-party app asks for an email or SMS confirmation code and keeps the exchange together with `auth_session` (Appendix A.4, A.5).
- An app whose refresh token is rejected a week later prompts for an OTP instead of a full re-login (Appendix A.6, B.4).
- A resource server demands a higher `acr` level and the app completes step-up in place (Appendix A.7).
- An app builds a registration flow that collects an email address and a phone number and creates the account on the fly (Appendix A.8).

## Why This Matters Now

- **Trigger**: The Datatracker lists revision 04 with the states "Active", "I-D Exists" and "WG Consensus: Waiting for Write-Up". `subject.json` gives no further reason (`ai_note` is empty).
- **Source evidence**: Appendix D lists -04 as "Editorial clarifications and improvements" and "Updated HTTP response codes for consistency". The diff shows the response-code change is normative in effect: `insufficient_authorization` and `redirect_to_web` now MUST use 403.
- **Expected impact**: Implementers following -03 examples that returned 401 or 400 for these errors need to change them. Whether the working group sees the write-up state as near publication is not stated in the material.

## What Changed

Changes from -03 to -04, from `diff.txt`:

- Section 5.2.2.1: `insufficient_authorization` and `redirect_to_web` MUST be returned with HTTP 403 (Forbidden). The general rule in Section 5.2.2 stays HTTP 400 unless a particular error code says otherwise.
- Section 5.2.2.1.1: a new `redirect_to_web` example with a `request_uri`, and a new SHOULD to follow [RFC9700] best practices including the `iss` response parameter of [RFC9207]. Both RFCs are added as informative references.
- Section 5.3.1: clients SHOULD discard the `auth_session` when the user logs out.
- Appendix B: the `otp_required` example now uses 403 instead of 401, and the sentence mandating 401 was removed.
- Section 5.1: the request example now shows `response_type=code`.
- Section 10.1: the IANA specification pointer is now Section 5.3.1, and Section 10.2 now points to Section 8. The earlier text referred to Section 5.4 and Section 4.1.
- Section 5.2.2: JSON is now cited as [RFC8259]. The [RFC7159] reference was removed.
- References: cross-device-security moves to -16 and attestation-based-client-auth to -09.
- The remaining changes are wording and editorial fixes, plus two acknowledgments (Filip Skokan, Joseph Heenan).

Compatibility: deployments that returned 400 or 401 for the two error codes would not conform to -04. The material does not say whether any deployed implementation did so.

## Technical Analysis

**Threat model.** Section 9 lists the risks the draft acknowledges:

- Phishing: a malicious app can impersonate the client, and users must learn a second place where credentials are entered (Section 9.2). The server MAY force a redirect-based flow at any stage.
- Credential stuffing and brute force at the new endpoint: implementers SHOULD apply controls like those on browser flows, use attestation APIs when possible, and rate-limit per `auth_session` (Section 9.3).
- Client impersonation: mobile and desktop apps are public clients, so the draft advises attestation (Section 9.4). If client authentication is required at the token endpoint, it MUST also be required at the challenge endpoint (Section 4.1).
- Verifying "first-partyness" is a MUST (Section 5) but the mechanism is left out of scope (Section 9.1).
- Token theft: tokens SHOULD be sender-constrained, and with DPoP the client SHOULD bind the authorization code by sending the DPoP header on the challenge request, with the server enforcing the same key on every later request and the token request (Section 9.5.1).
- `auth_session` hijacking: the value SHOULD be bound to the device, for example to the DPoP key (Section 5.3.1, 9.6.1). It needs at least 256 bits of entropy if random, and its lifetime is up to the server (Section 9.6.2).

**Protocol flow.** The design reuses the existing token endpoint and only issues authorization codes at the new endpoint (Appendix C). The draft gives two reasons: fewer changes to existing OAuth servers, and a closer match to the redirect-based flow. It rejects per-factor grant types and returning tokens directly.

**Interop implications.**

- The draft states that the client-server interaction is intentionally unspecified, so two independent implementations will not interoperate without a shared profile (Section 1.2, Appendix B).
- Extension parameters that have no meaning outside a browser, such as `response_mode=query`, are handled in an unspecified way (Section 4.1).
- The AS-defined error codes and custom values are explicitly out of scope (Section 5.2.2).
- Browser-based apps are NOT RECOMMENDED (Section 9.8).

## Open Questions

- Section 5.2.2.1 gives no status code for `invalid_session`, so Section 5.2.2 defaults to 400 for it. The draft does not say whether that is intended.
- Section 6.2 shows HTTP 403 at the token endpoint, while the draft cites Section 5.2 of [RFC6749] for the error format. The draft does not say how this interacts with [RFC6749] error handling at that endpoint.
- Section 10.1 registers `auth_session` with usage location "token response" only, although it also appears in challenge endpoint error responses (Section 5.2.2, 6.2) and requests (Section 5.1). Whether the registration should cover these is not discussed.
- The references list contains `[IANA.JWT] "*** BROKEN REFERENCE ***"`, and the terminology section still contains "TODO: Replace RFC6749 references with OAuth 2.1" (Section 2.1).
- Section 9.1 requires verifying first-partyness but gives no concrete mechanism. The draft only suggests attestation and client authentication as options.
- Section 7 says the client sends `acr_values`, `max_age` and `scope` to the challenge endpoint, while Section 5.1 does not list `acr_values` or `max_age` as parameters. They would come through the extension rule in Section 4.1.
- The draft says it is intended to be profiled (Section 1.2), but no profile is named in the material.

## Experiments

- [ ] Stand up a minimal challenge endpoint with the Appendix B username and OTP profile, and confirm that a client library handles a 403 `insufficient_authorization` response followed by a 200 `authorization_code`.
- [ ] Add DPoP: send the header on the first challenge request, then switch the key on the second request and on the token request, and check that the server rejects both (Section 9.5.1, 9.6.1).
- [ ] Return `redirect_to_web` with and without a `request_uri`, with and without a `code_challenge` in the first request, and check that the server never returns a `request_uri` when no PKCE challenge was sent (Section 5.2.2.1.1).

## Sources

- [draft-ietf-oauth-first-party-apps-04 on the IETF Datatracker](https://datatracker.ietf.org/doc/draft-ietf-oauth-first-party-apps/04/)
- [Source repository named in the draft](https://github.com/oauth-wg/oauth-first-party-apps)
