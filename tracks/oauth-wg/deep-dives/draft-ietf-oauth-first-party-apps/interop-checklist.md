# Interop Checklist

- [ ] The challenge endpoint URL uses the `https` scheme and accepts `application/x-www-form-urlencoded` POST bodies in UTF-8 (Section 4.1).
- [ ] Requests without `response_type=code` are rejected, and `client_id` is treated as required unless the client is identified by authentication or `auth_session` (Section 5.1).
- [ ] If both `client_id` and an authenticated or session-derived client identity are present and differ, the request is rejected (Section 5.1).
- [ ] If the server requires client authentication at the token endpoint for a client, it also requires it at the challenge endpoint (Section 4.1).
- [ ] `insufficient_authorization` and `redirect_to_web` are returned with HTTP 403, and a client written for 400 or 401 still handles them (Section 5.2.2.1, Appendix B).
- [ ] The status code for `invalid_session` and for other errors is 400 by default, and the client does not rely on a different code (Section 5.2.2).
- [ ] `error`, `error_description` and `error_uri` contain only the allowed ASCII characters (Section 5.2.2).
- [ ] The client sends the stored `auth_session` on every later challenge request and replaces it when a response carries a new value (Section 5.3.1).
- [ ] An `auth_session` presented from a different device, or with a different DPoP key, is rejected (Section 5.3.1, 9.6.1).
- [ ] The client does not assume any `auth_session` lifetime, and it discards the value on logout (Section 5.3.1, 9.6.2).
- [ ] With DPoP, the same key is required on every challenge request and on the token request, and a different key is rejected (Section 9.5.1).
- [ ] `redirect_to_web` never carries a `request_uri` when the first request had no `code_challenge` (Section 5.2.2.1.1).
- [ ] When `redirect_to_web` has no `request_uri`, the client starts a normal authorization code flow with PKCE (Section 5.2.2.1.1).
- [ ] The token request carries no `redirect_uri` and the token response may carry `auth_session` (Section 6, 6.1).
- [ ] A refresh token request can return 403 `insufficient_authorization`, and the client continues at the challenge endpoint (Section 6.2).
- [ ] After an [RFC9470] error from a resource server, the client sends `acr_values`, `max_age` and `scope` at the challenge endpoint (Section 7).
- [ ] The authorization server metadata publishes `authorization_challenge_endpoint` (Section 4.1, 8).
- [ ] Rate limiting is applied per `auth_session`, and an AS-defined profile exists for the extra parameters and error codes in use (Section 9.3, Appendix B).
