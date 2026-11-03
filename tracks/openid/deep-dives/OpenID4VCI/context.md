# Context

## Trigger

`subject.json` gives no reason for picking this repository (`ai_note` is empty). It is a repository on the `openid` track, and its README and recently updated pull requests were staged.

## Why This Matters

OpenID4VCI is the specification for how holders request credentials and issuers issue them. The recent pull requests show ongoing work on the 1.1 draft and a new Server to Server draft, including renamed error fields, session binding rules and deferred issuance. Anyone implementing a wallet or an issuer needs to know which draft and which pull requests they are building against.

## Open Questions

- The staged material holds no draft text, so every statement here rests on pull request titles. Which pull requests change normative behavior?
- Which draft (1.0, 1.1 or s2s) is the one implementers should target now?
- What are the s2s draft's scope and its relation to the wallet-facing drafts?
