# Context

## Trigger

The drafting pipeline recorded no reason for the pick. OpenID4VP was the second `openid` candidate in `tracks/openid/data/normalized/candidates.json` without a deep dive. The daily briefing in `tracks/openid/data/normalized/insights.json` recorded the merge of #800 (branch `718-age-over-nn`) without its diff. #800 merged on 11 November 2026 and adds the `age_over_NN` data element selection rule to both the 1.0 errata draft and 1.1 (Section B.2.5 in both). This deep dive was checked against the 1.0 Final text (tag `1.0-final`), the drafts at commit `66f5ff9` (11 November 2026), and the pull requests and issues it cites.

## Why This Matters

OpenID4VP 1.0 is an OpenID Final Specification (announcement dated 10 July 2025) and is the presentation half of the OpenID4VC family. Work has moved to two places: a 1.0 errata draft (revision `-31`, 26 changes in its Document History) and 1.1 (revision `-01`), which adds HPKE response encryption, stricter type matching and DC API Origin requirements. Several errata changes are visible on the wire: `alg: none` Request Objects for the `redirect_uri` prefix, no empty VP Token, the GET fallback for `request_uri_method`, and a different `age_over_NN` element in an mdoc response. An implementer has to know which text a peer follows.

## Open Questions

- When will the `1.0/` draft be approved as errata set 1, and will the open #803, #808 and #726 be in it?
- Will #808 replace the `transaction_data` rejection rule that #790 clarified?
- How will Verifiers handle a different `age_over_NN` identifier, given that the rule is a SHOULD (errata Section B.2.5)?
- Which profiles require Wallets to validate request signatures over the DC API, where Section 5.9.3 leaves it to the Wallet?
