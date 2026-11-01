# Context

## Trigger

The pipeline picked draft-ietf-oauth-identity-assertion-authz-grant at revision -06 (track: oauth-wg; Datatracker states: Active, I-D Exists, WG Document). The stated reason in `subject.json` is that -06 adds new normative behaviour (client authentication at the IdP, `invalid_request`, mTLS binding, new metadata) and a large rewrite. The OAuth list announcement from the author says the same changes are mostly clarifications from implementation feedback and that the flow and overall design are unchanged.

## Why This Matters

ID-JAG, informally Cross-App Access (XAA), moves the decision to broker app-to-app API access to the IdP that both applications already use for SSO. The draft's own use cases include enterprise SaaS integrations, customer identity platforms, email and calendar clients, and AI agents calling external tools (Appendix A). Because the grant is redeemed without a user prompt, the security of the whole chain depends on correct client authentication, token typing, audience and resource checks, tenant handling and, optionally, sender constraining. Several of these rules were tightened in -05 and -06, so independent implementations are the ones most likely to differ. The authors say there are now many implementations across IdPs, authorization servers, clients and libraries.

## Open Questions

- Settled by comparing the texts: the IdP client-authentication rule, the single-audience rule and Privacy Considerations entered the body in -05 (none is in -04). -06 completed the Document History and changed the subject-token error code.
- How should clients tell the two error endpoints apart in retry logic, given `invalid_request` at the IdP and `invalid_grant` at the Resource Authorization Server for expired inputs (Sections 4.3.4.3 and 4.4.3)?
- Which of the 20 open issues in the working group repository (for example #141, #142, #145, #129 and #114) the author will bring to IETF 127. The announcement does not say.
- Whether the draft's reliance on two Work in Progress drafts (Identity Chaining and the DPoP JWT grant) will cause changes here as they move.
