# Context

## Trigger

The repository was picked because of this note: 23 commits in four days, including a field rename and credential_types becoming an array. The track is `openid`.

## Why This Matters

The repository is the working area of the OpenID Foundation's Digital Credentials Harmonized Presentation Working Group, which supports a joint initiative with ISO/IEC JTC 1/SC 17 (WG10) and the DCP Working Group. Its aim is to harmonize ISO/IEC 18013-5 Device Request / Device Response with OpenID for Verifiable Presentations Authorization Request / Authorization Response, for in-person and online presentation, including ISO mdoc and IETF SD-JWT VC. Fast changes to field names and shapes affect anyone implementing from the Editor's Copy, which the README says is not an approved Working Group Draft.

## Open Questions

- What do the 23 commits change on the wire? The staged material has only the README and pull request titles, so the exact scope is not confirmed.
- How will security considerations be written, given that pull request #85 adds only a placeholder?
- Which of the open pull requests (#64, #65, #76, #77, #81, #83) will be accepted, and in what form?
