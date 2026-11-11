# Context

## Trigger

- Event detected by radar: "23 commits in four days, including a field rename and credential_types becoming an array" (track `openid`). On `main` this was two rebase-merged pull requests. #61 landed 8 commits on 4 November 2026 and made `credential_type` an array. #57 landed 23 commits on 9 November 2026: format details moved into per-format annexes and `CredentialItem.format` was renamed `credential_format`.
- Related repository / PR / Issue: <https://github.com/openid/dchp>, pull requests #57 and #61, issue #46.

## Why This Matters

The repository is the working area of the OpenID Foundation's Digital Credentials Harmonized Presentation Working Group. The specification's Foreword says the text is developed jointly by members of ISO/IEC JTC 1/SC 17 WG 10 and the OpenID Foundation DCP Working Group. It defines one CBOR request and response model with a transcript-based channel binding. The model is meant to work over ISO/IEC 18013-5 proximity sessions, OpenID4VP and the Digital Credentials API, for both ISO mdoc and SD-JWT VC. The text is an Editor's Copy without working group consensus on its core clauses, and several open pull requests (#76, #77, #81) would change integer keys, structures or names. Anyone implementing it now has to pin a commit.

## Open Questions

- Will the prose and the CDDL be aligned before any WG Draft? Today they disagree on `ChannelBinding` keys and on `purpose_id` (`controller_id` in the prose, `controlled_id` in the CDDL). Open pull request #76 fixes this.
- How will the transcript be carried into the mdoc `SessionTranscript`, and how will the KB-JWT `nonce` and `aud` be encoded (issue #10)?
- When will the first Working Group Draft be published (issue #72, deferred on 4 November 2026 by about one to two months), and through which ISO/IEC route (issue #13: PAS or PSDO)?
