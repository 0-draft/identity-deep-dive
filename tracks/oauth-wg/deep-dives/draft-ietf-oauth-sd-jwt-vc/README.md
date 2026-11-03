# Deep Dive: draft-ietf-oauth-sd-jwt-vc

> In one line: SD-JWT VC profiles SD-JWT (RFC 9901) as a credential format by adding a type identifier (`vct`), two ways to find the Issuer's key, and optional Type Metadata for display and claim rules.

## What this is

SD-JWT (RFC 9901) gives JWTs selective disclosure but does not say which claims a credential carries or what they mean (Section 1.2). This draft fills that gap for Verifiable Digital Credentials, which it calls SD-JWT VCs. It defines the `application/dc+sd-jwt` media type and the `dc+sd-jwt` `typ` header value (Sections 2.1 and 2.2.1), and new claims `vct` (the credential type) and `aka_vcts` (further types) (Sections 2.2.2.1 and 2.2.2.2). It also defines two Issuer key discovery mechanisms, JWT VC Issuer Metadata under a well-known URI and inline `x5c` certificates (Sections 2.5 and 4). Finally it defines Type Metadata, a JSON document found through `vct` that carries display, rendering and claim rules (Section 5). Because these documents are fetched from URLs taken from untrusted credentials, a large part of the draft is HTTP retrieval and SSRF (server-side request forgery) rules (Sections 3 and 7.1).

## How it works

```mermaid
sequenceDiagram
    participant I as Issuer
    participant H as Holder
    participant V as Verifier
    participant M as Issuer metadata endpoint
    participant T as Type Metadata publisher
    I->>H: SD-JWT VC with typ dc+sd-jwt, vct, optional cnf and Disclosures
    H->>V: SD-JWT VC with chosen Disclosures and optional KB-JWT
    V->>V: Process per RFC 9901 Section 7
    V->>M: GET well-known jwt-vc-issuer for the iss value
    M-->>V: Issuer metadata with jwks or jwks_uri
    V->>V: Verify Issuer signature with a permitted key mechanism
    V->>T: Optional GET of Type Metadata from the vct URL
    T-->>V: Type Metadata JSON
    V->>V: Check integrity, extends chain and claim metadata
```

1. The Issuer signs an SD-JWT whose header has `typ` set to `dc+sd-jwt` and whose payload has a `vct` claim. Claims are selectively disclosable except those the draft forbids hiding, such as `iss`, `exp`, `cnf` and `vct` (Sections 2.2.1 and 2.2.2.3).
2. The Holder presents the SD-JWT with only the Disclosures it chooses, and a KB-JWT (Key Binding JWT) when Key Binding is required. The KB-JWT is checked against the `cnf` claim (Sections 2.3.2 and 2.4).
3. The recipient processes the SD-JWT as RFC 9901 Section 7 describes. The Issuer check in RFC 9901 Section 7.1 point 2.c is satisfied by a key discovery mechanism that policy permits for that Issuer (Section 2.4).
4. When `iss` is an HTTPS URL, the recipient can fetch the metadata from the well-known URI `/.well-known/jwt-vc-issuer` inserted between host and path, and take the keys from `jwks` or `jwks_uri`. The returned `issuer` must equal `iss` (Sections 4, 4.1 and 4.3).
5. Alternatively, when the protected header has `x5c`, the end-entity certificate's key is used and the chain is validated against a trust anchor permitted for the Issuer (Section 2.5).
6. A Holder or Verifier MAY then process Type Metadata. If it does, it follows `extends`, verifies any `#integrity` values, validates the payload against the claim metadata (`path`, `mandatory`, `sd`) and rejects the credential on failure (Sections 5.3, 5.4, 5.6, 5.7 and 6).

## Use cases

- A government issues a person identification credential. A wallet presents only an age claim and the nationality to a Verifier, as in the Appendix A.1 example based on the EUDI Wallet (European Digital Identity Wallet) Architecture and Reference Framework.
- A Verifier built into a service must decide whether to trust an Issuer. It selects between JWT VC Issuer Metadata and `x5c` according to its policy for that Issuer (Sections 2.5 and 7.3).
- A credential type is published by a standards body or community and is extended by national types. Verifiers use `vct`, `aka_vcts` and `extends` to match types, and still check Issuer authorization separately (Sections 2.2.2.2, 5.4 and 7.7).
- A wallet renders a credential from Type Metadata, using a logo, a background image or an SVG template with `{{svg_id}}` placeholders, and must escape values and sandbox the SVG (Sections 5.5.1 and 7.10).
- An operator runs a service that resolves `iss` and `vct` URLs and needs the redirect, size, time and internal-address rules to avoid SSRF (Sections 3 and 7.1).

## Why This Matters Now

- **Trigger**: The ART-ART telechat review returned Ready, so the draft is moving toward publication (`subject.json`). The Datatracker states listed there include "IESG Evaluation" and "Submitted to IESG for Publication".
- **Source evidence**: The mailing list shows the review of -23 by Christian Amsüss with result Ready, which says all previously raised issues were addressed. It also shows Mike Bishop's DISCUSS and Mahesh Jethanandani's No Objection with comments on -23 (`mail.txt`). So Ready from one directorate review does not mean the IESG is finished.
- **Expected impact**: The draft is a Standards Track format used for wallet credentials, and its Type Metadata and retrieval rules affect any implementation that fetches credential metadata. If the DISCUSS leads to an `Updates: RFC 7800` relationship or a rewording of Section 2.2.2.3, it changes how key-bound credentials without `sub` or `iss` are described. Which outcome will be chosen is not shown in the material.

## What Changed

- Spec/document change summary: Revision -23 contains no visible change to normative text (`diff.txt`). It refreshes the expiry date to 4 May 2027 and the draft date to 31 October 2026. It regenerates the example signatures in Figures 7, 8, 10 and 26 and the Appendix A.1 examples. The KB-JWT `iat` and `sd_hash` values in Figures 8, 26 and 27 change too. Editorial fixes are a `text_color` wording fix in Section 5.5.1.1, "in by [RFC8615]" becoming "in [RFC8615]" in Section 9.3, and a stray trailing slash removed from the OWASP URL. Su-hyeon Forten Lee is added to the acknowledgements, and the history lists only "some minor fixes" for -23. The diff also adds and removes blank lines in the document history without changing its text.
- Earlier revisions give the context for the open ballot items. Per the document history, -22 answered IESG ballot comments from Ketan Talaulikar and stated the RFC 7800 `sub`/`iss` departure, -21 limited which claim metadata failures reject a credential, -20 added `aka_vcts` guidance and the `x5c`/`iss` clarification, and -19 added the general HTTP retrieval section.
- Compatibility or migration concerns: None at protocol level are visible in -23. Test vectors copied from -22 differ in signatures and `iat`/`sd_hash`. Whether the new example signatures verify was not checked here. The history of -19 shows that the transitional note about accepting `vc+sd-jwt` as `typ` was removed, so the current text names only `dc+sd-jwt`.

## Technical Analysis

- Threat model implications: `iss`, `vct`, `jwks_uri`, `extends` and `uri` values come from untrusted input, so the Consumer must validate every URL, including each redirect target, against internal and non-globally-reachable addresses, and bound time and size (Sections 3 and 7.1). Type and Issuer claims are only as trustworthy as the Issuer: neither `extends` nor `aka_vcts` implies authorization to issue a type (Sections 2.2.2.2 and 7.7). Type Metadata is trusted only as far as its Publisher is (Section 7.8). Display text and SVG templates are attack surfaces for injection and active content (Sections 5.5.1.2.2, 7.6 and 7.10), and data URIs are untrusted input (Section 7.9). Verifiers must ensure an attacker cannot choose the verification mechanism for a given `iss` (Section 7.3). `extends` cycles must be detected (Section 7.4). Privacy risks include a Holder-specific `iss` used for phone-home, remote key retrieval in `cnf`, the non-selectively-disclosable `vct` and `aka_vcts`, and tracking through metadata fetches (Sections 8.2, 8.3 and 8.4).
- Protocol flow implications: Verification is RFC 9901 processing plus a policy-permitted key mechanism (Sections 2.4 and 2.5). Type Metadata processing is optional unless policy or ecosystem rules require it, and then failure to retrieve or validate means rejection (Section 5.7). Integrity-keyed caching can be indefinite, otherwise HTTP caching under RFC 9111 applies (Sections 3, 5.3.4 and 6). Claim metadata is evaluated against the issued payload including undisclosed array positions, and a Verifier MUST NOT read the absence of a disclosable claim as a missing mandatory claim (Section 5.6).
- Interop concerns: Both an HTTPS `iss` and `x5c` can appear in one credential, and Section 2.5 says only that the mechanism must be permitted by policy and that `iss` need not match the certificate. Section 7.3 requires the `iss`-to-key relationship to be maintained. Extending types may tighten but not loosen `sd` and `mandatory` (Section 5.6.5.1), while `display` is replaced rather than merged (Sections 5.5.2 and 5.6.5). `#integrity` uses the W3C SRI string syntax but its own verification procedure, with no CORS dependence (Section 6). The IANA sections still contain placeholder document references (Section 9).

## Open Questions

- Section 2.2.2.3 says the draft "explicitly overrides" the RFC 7800 requirement that a `cnf` JWT also carry `sub` or `iss`, and no `Updates:` header is shown. Mike Bishop's DISCUSS asks about this, and Mahesh Jethanandani supports it. Whether the resolution is an `Updates` relationship or a rewording is not shown.
- Section 7.1 names private-use ranges and Consumer-internal hosts as forbidden unconditionally. A comment on the ballot asks whether configured allow-lists should be permitted for closed or enterprise deployments. The draft does not say so.
- Section 2.5 and Section 7.3 may pull in different directions when `x5c` and an HTTPS `iss` are both present, and the draft does not say which mechanism applies beyond "permitted according to policy". A ballot comment also asks that the `x5c` validation be tied to RFC 5280 through RFC 7515 Section 4.1.6. These points come from the mail, not from the draft.
- Section 4.2 and Section 5.3.1 use `application/json` for metadata. A ballot comment encourages distinct media types. Section 4.3 might state that the `issuer` check applies across redirects.
- Section 5.5.1.2.1 uses a MUST for choosing among SVG templates that a comment calls not an interop requirement. Section 5.5.1.2.2 needs a normative pointer to SVG structure. Section 7.6 has a MUST that a comment says is hard to test.
- The ballot messages are truncated in the staged mail, so further comments from Mahesh Jethanandani and Mike Bishop may exist that are not covered here.

## Experiments

- [ ] Lab 1: Build a verifier that takes an SD-JWT VC with both an HTTPS `iss` and an `x5c` header and runs it under three policies (metadata only, `x5c` only, both permitted). Record which keys are used and when it rejects, to see how Section 2.5 and Section 7.3 behave.
- [ ] Lab 2: Point a test `iss`, `jwks_uri`, `vct` and logo URL at loopback, link-local and private addresses, at a DNS name that resolves internally, and at a redirect chain that ends on an internal or `http` URL. Check that a Consumer following Section 3 and Section 7.1 refuses each one.
- [ ] Lab 3: Create a Type Metadata chain with `extends`, `extends#integrity` and claim metadata where the child tries to loosen `sd` or `mandatory`, plus a cycle. Present credentials with and without the relevant Disclosures and check the rejections required by Sections 5.6, 5.6.5.1 and 7.4 and the rule that absence is not proof of a missing mandatory claim.

## Sources

- <https://datatracker.ietf.org/doc/draft-ietf-oauth-sd-jwt-vc/23/>
- <https://mailarchive.ietf.org/arch/msg/oauth/rShUO7YVi2WyKSxydiyWt5eonUc/>
- <https://mailarchive.ietf.org/arch/msg/oauth/5yaIITzC7JvwuRt94lpF7u4P72E/>
- <https://mailarchive.ietf.org/arch/msg/oauth/d49b8f7_xsSOXCgDit-a1p9-yvg/>
- <https://mailarchive.ietf.org/arch/msg/oauth/DNuSXwlB4yGxuTGQigaG7tcZf7A/>
