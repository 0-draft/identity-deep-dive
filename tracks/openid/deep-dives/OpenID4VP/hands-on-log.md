# Hands-on Log

## Environment

- Runtime: Python 3.15.2 (standard library only, run with `python3 -I`)
- Tooling: git 2.56.1, gh 2.104.0. No mmark or xml2rfc: the markdown source is compared directly, not the rendered text.
- Versions: a clone of `openid/OpenID4VP`. Base: tag `1.0-final` (commit `e819ed379abe9b0f6e93037e22d678837992e8b2`, 10 July 2025). Head: `main` at `66f5ff93130128d1662cc60fcd79185ffe0a2d30` (merge of #800, 11 November 2026), the newest commit on 18 November 2026, when the lab was run.

## Steps

1. Clone the repository and fetch the tags: `git clone https://github.com/openid/OpenID4VP` and `git -C OpenID4VP fetch --tags`. `git -C OpenID4VP rev-parse main` prints `66f5ff9…`.
2. Save the merged pull requests so merge commits map to PR numbers: `gh pr list -R openid/OpenID4VP --state merged --limit 400 --json number,title,mergeCommit,mergedAt,baseRefName > prs.json` (280 PRs).
3. Run `python3 -I vectors/errata_history_check.py OpenID4VP 1.0-final 66f5ff9 prs.json`. The script:
   - reads `openid-4-verifiable-presentations-1_0.md` at the root (Final) or under `1.0/` (after #699 moved it unchanged),
   - drops the front matter, fenced code blocks and the Document History, splits the rest into sections (heading anchor or title) and sentences, and normalizes whitespace,
   - treats a sentence with an RFC 2119 keyword in capitals as normative, and diffs Final against head: added, removed, changed (paired by similarity, split into keyword set changed or wording only), and moved to another section,
   - walks the 34 first-parent commits between the two that touched the 1.0 text or `1.0/examples/`, diffs each against its parent, records the Document History bullets it added, and gives each PR a status: `ok`, `NO HISTORY ENTRY` (a normative sentence changed, no bullet added), `HISTORY, PROSE CHANGE` (a bullet added, only sentences without a keyword changed), `HISTORY ONLY`, or no change of either kind.
4. Check that the script can fail. `python3 -I vectors/errata_history_check.py --self-test` (also run at the end of step 3) feeds nine altered copies of a small spec through the same code: whitespace only, a change inside a code block and a reordering inside a section must not be flagged; a `MAY` to `SHOULD` change, a new `MUST NOT` sentence and a keyword sentence moved to another section, each without a bullet, must give `NO HISTORY ENTRY`. Three mutants of the script, kept outside the repository, fail it: a keyword regex without `MUST` (2 of 9 cases fail, exit 1), code fences not skipped (1 fails), and moves not counted (1 fails, exit 1).
5. Read every flagged PR, and every `ok` PR whose diff has more than one normative sentence, against its bullet. `gh pr view <n> -R openid/OpenID4VP --json title,mergedAt,files,commits` for #719, #731, #735 and #745 confirms which commits each PR carried.

## Results

- The output is in `vectors/errata_history_check.log`. The self-test passes 9 of 9.
- Normative sentences: 379 in the Final, 404 in the errata draft. Final to head: 33 added, 8 removed, 4 changed with a different keyword set, 11 changed in wording only, 2 moved to another section (58 in all). Every one is attributed to a PR.
- The 26 bullets under `-31` come from 23 PRs (#719, #745 and #790 add two each). Each bullet matches a change in the text of its PR. No bullet describes a change that is not there.
- 34 PRs touched the 1.0 text or examples. 18 are `ok`. 5 added a bullet for a change with no keyword in it (#698 scope of `encrypted_response_enc_values_supported`, #724 "Verifier Info", #729 `invalid_scope` removed, #730 absent `intent_to_retain`, #801 new `invalid_request` case). #700 only added the `-31` placeholder and the `-final` link. 8 changed no normative sentence and added no bullet: #699 (file move), #663 (example claim names), #712 (formal analysis references), #725 (an example file), #728 (`scope` in the intro), #775 (cross-reference), #776 (`openid_federation` in an error example), #787 (`ldp_vc` example caption).
- Normative changes with no Document History entry:
  - #735 (merged 22 September 2026) has no bullet at all. It removes five MUSTs that Verifier metadata (other than the key, for signed prefixes) comes from `client_metadata`, one each for `redirect_uri`, `decentralized_identifier`, `verifier_attestation`, `x509_san_dns` and `x509_hash` in Section 5.9.3, and adds the "Source of Verifier Metadata" section (errata Section 14.12) with a MAY for profiles to define more `client_metadata` parameters, a RECOMMENDED that they are safe to use untrusted, and a MAY to use other trusted sources. The 1.1 Document History has no entry for it either.
  - #745 moved the two "SHOULD NOT return any OpenID4VP protocol errors" sentences from the DC API privacy section (Final Section 15.9.2) to a general "Error Responses" section (errata Section 15.9), so they now apply to every invocation method. Its two bullets cover only the empty VP Token and the editorial rewrite of `vp_token`.
  - #719 added two MUST NOTs on `expected_origins` values: no `ftp`, `javascript`, `data`, `ws` or `wss` scheme, and no `http` outside development (errata Section A.2). Its two bullets cover the string comparison and the trusted platform.
- #731 is flagged `NO HISTORY ENTRY`, but the only change ("a list of name/value pairs" to "name/value pairs" in `vp_formats_supported`) is editorial.

## Failure Modes

- Keyword-only matching misses normative prose without a keyword, such as #730's "If absent, the Verifier makes no statement" and #801's new `invalid_request` case. The `HISTORY, PROSE CHANGE` status and the prose diff in the log cover them, but each needs reading.
- A move between sections is a normative change when it widens scope (#745). An earlier version of the script ignored moves and missed it.
- Short fragments: `` `state` is OPTIONAL. `` has fewer than five words and is joined to the next sentence, so #734 shows as one changed and one added sentence instead of one changed.
- Similarity pairing across PRs: in the Final-to-head list, the removed `redirect_uri` sentence of #735 is paired with the `encrypted_response_enc_values_supported` entry that #802 added, because both mention `client_metadata` and (#new_parameters). The per-PR lists pair within one PR and show it correctly as a removal.
- Only the 1.0 markdown and `1.0/examples/` are compared. A change that exists only in the rendered output, such as a reference version resolved by mmark (#726, open), is not seen.

## Next Actions

- Raise the missing #735 entry, and the parts of #745 and #719 that their bullets do not mention, with the OpenID4VP editors before errata set 1 is approved.
- Re-run the script on the head that is approved as errata set 1, after #803, #808 and #726 are decided.
- Experiments 2 to 5 stay open: they need a real Wallet (an mDL with `age_over_NN`, `request_uri_method` handling, HTTP 307 on the Request URI and Response URI) or the OpenID conformance suite, and none was available. A local script that applies the parsing rules would not test a Wallet.
