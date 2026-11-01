# Context

## Trigger

The pipeline picked draft-ietf-oauth-identity-assertion-authz-grant at revision -06 (track: oauth-wg; Datatracker states: Active, I-D Exists, WG Document). The stated reason in `subject.json` is that -06 adds new normative behaviour (client authentication at the IdP, `invalid_request`, mTLS binding, new metadata) and a large rewrite. The OAuth list announcement from the author says the same changes are mostly clarifications from implementation feedback and that the flow and overall design are unchanged.

## Why This Matters

ID-JAG, informally Cross-App Access (XAA), moves the decision to broker app-to-app API access to the IdP that both applications already use for SSO. The draft's own use cases include enterprise SaaS integrations, customer identity platforms, email and calendar clients, and AI agents calling external tools (Appendix A). Because the grant is redeemed without a user prompt, the security of the whole chain depends on correct client authentication, token typing, audience and resource checks, tenant handling and, optionally, sender constraining. Several of these rules were tightened in -05 and -06, so independent implementations are the ones most likely to differ. The authors say there are now many implementations across IdPs, authorization servers, clients and libraries.

## Open Questions

- Which of the Document History items listed under -05 appear in the -05 body text and which were first written into the body at -06? The staged diff covers only -05 to -06 and is marked truncated.
- How should clients tell the two error endpoints apart in retry logic, given `invalid_request` at the IdP and `invalid_grant` at the Resource Authorization Server for expired inputs (Sections 4.3.4.3 and 4.4.3)?
- What are the "remaining open issues" the author plans to discuss at IETF 127? The staged material does not list them.
- Whether the draft's reliance on two Work in Progress drafts (Identity Chaining and the DPoP JWT grant) will cause changes here as they move.
