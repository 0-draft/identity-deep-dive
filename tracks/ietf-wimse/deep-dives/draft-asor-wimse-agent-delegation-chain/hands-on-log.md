# Hands-on Log

## Environment

- Runtime: Python 3.15.2, run as `python3 -I` (printed on the first line of every log in `vectors/`)
- Tooling: Python stdlib and `cryptography` 50.0.2 (Ed25519 only). Every script in `vectors/` was written for this log from the draft text; no code from attenu-guard, attenu-guard-ts, Cred or tenuo was run. `gh` was used once, to fetch the niyikiza text.
- Versions: draft-asor-wimse-agent-delegation-chain-03 (text file sha256 `270e28cb1448c0bdd14c04907932bba8a9b857574d26cf1ce9d54f704e1474df`); the 36 Appendix B vector JSON files from attenu-guard tag v0.22.0 (HS256 test signer, secret and kid inside each file; aggregate hash in `vectors/verify_vectors.log`), read as data; draft-niyikiza-oauth-attenuating-agent-tokens-02 from `ietf/` in tenuo-ai/tenuo at `main` = `63ed003934f1d452601164965e6ab3b6ca23fc43` (sha256 `a7e23c35362c1fb60018a63343f8b0fdc1ce4a8c01fbf73af4a85e7ecf79f0f2`)
- Date: 18 November 2026

## Steps

1. Put the -03 text and the 36 vector files in a local directory `attenu-guard-v0.22.0-draft02/`, outside the repository.
2. Score the vectors: `python3 -I vectors/verify_vectors.py <dir>/attenu-guard-v0.22.0-draft02 > vectors/verify_vectors.log`. The script implements the parse rules of Sections 3, 4, 4.1, 4.2 and 4.4, steps 1 to 5 of Section 6, and the audience part of step 8. It then runs its self-test: the unmodified `valid_chain.json` plus 12 mutations of it, each expected to give a named outcome.
3. Lab 1: `python3 -I vectors/three_hop.py > vectors/three_hop.log`. It mints a three-token chain (planner, researcher, formatter) with alg `Ed25519` from fixed seeds and runs steps 1 to 5 only.
4. Lab 2: `python3 -I vectors/overspend.py > vectors/overspend.log`. It mints root max 100 with two children at 60, verifies both chains, then models two gateways, a shared ledger and a single-writer allocator in-process (threads stand in for the two gateways).
5. Lab 3: fetch the niyikiza text with `gh api repos/tenuo-ai/tenuo/contents/ietf/draft-niyikiza-oauth-attenuating-agent-tokens-02.txt -H "Accept: application/vnd.github.raw"`, then `python3 -I vectors/depth_rules.py > vectors/depth_rules.log`. It implements only the depth checks of niyikiza-02 Section 8 (steps 3c, 3i, 4b4, 4d to 4g, 4m and 5, with MAX_DELEGATION_DEPTH 8) and the asor depth rules, and also runs each case through the full asor verifier on a minted chain.
6. `python3 -m compileall -q vectors/*.py`.

## Results

- Vectors: 36 of 36 matched their expected outcome name. Per name: accept 5/5, malformed 17/17, not_narrower 8/8, par_hash_mismatch 2/2, principal_altered 1/1, signature_invalid 1/1, expired 1/1, audience_mismatch 1/1. Steps not performed: 6 (DPoP holder binding), 7 (status list) and the action part of 8 (scope, per-action and cumulative constraints). No vector expects an outcome from those steps, so no vector was skipped. The self-test gave the expected name for the unmodified chain and all 12 mutations, including non_canonical, duplicate_member and non_finite, which no file in the set exercises.
- The score depends on four readings the -03 does not fix. (1) A child that omits "del_max_depth" inherits its parent's value for rule 5. Section 3 requires the claim only in DT_0, and rule 5 says nothing about a missing value. In `reject_child_raises_del_max_depth.json` DT_1 has no claim and DT_2 carries 60, so a verifier that compares only adjacent tokens carrying the claim accepts it. (2) "cnf" must carry "jkt", because Section 7 says the claim carries the JWK thumbprint. (3) The parse checks run on every token before step 1, following Section 4.4. (4) Step 1 names no key for DT_i with i > 0, so every token is verified under the one trusted key (single signer, as in Section 11).
- Vector metadata: the description of `reject_child_raises_del_max_depth.json` says "a root bound of 6", but its DT_0 carries "del_max_depth" 7. The outcome name is unaffected. Every file carries `"draft": "02"`, including `reject_child_adds_detail_type.json`, which Appendix B says was added in the -03.
- Lab 1: 17 of 17 cases gave the expected name: not_narrower (scope added, max_rows widened, max_rows dropped, del_max_depth raised), principal_altered, par_hash_mismatch (re-issued parent, parent swapped), expired, signature_invalid and depth_invalid. At the boundary, with DT_2 exp 1900, now 1899 accepts, now 1900 gives expired under the -03 rule (now < exp), and now 1900 accepts under the -02 rule (now <= exp). A child exp above its parent's is reported as expired at step 5, not not_narrower.
- Lab 2: with root max 100 and two children at 60, both chains verify and the two gateways permit a combined 120. A single child at 120 is not_narrower. With max_subtree 100 at the root and 60 + 60 at the children, both chains still verify, because each edge is narrower. A gateway that holds no subtree total denies (spend 0); one that skips the cumulative check spends 120. An atomic check-and-debit ledger gave 60 in all 500 two-gateway races. A ledger that reads at authorization and debits afterwards (with the interleaving forced) gave 120 in 50 of 50. Two uncoordinated ledger replicas gave 120. A single-writer allocator granted 60 to A, refused a further 60 to B, then granted 40 to B, and the gateways honored 100 in total. Each hazard reproduced: duplicate allocation by two offline allocators gave 120 allocated; local rollback of a debit that was not persisted let gateway A honor 120 against 60 (refused when the debit is persisted first); premature reuse of a reservation released before settlement let gateway B honor 80 against 40 (refused while the reservation is held).
- Lab 3: 5 of the 10 named cases disagree. (a) Leaf "del_depth" equal to the root's "del_max_depth" (2, 2): asor depth_invalid, niyikiza accepts. (b) Root "del_max_depth" 0: asor malformed (must be positive), niyikiza accepts a terminal root. (c) Children without "del_max_depth": asor accepts, niyikiza denies at 4b4. (d) DT_1 lowers "del_max_depth" to 1 and DT_2 sits at depth 2 under root 5: asor accepts, niyikiza denies at 4e. (e) Root 9 above MAX_DELEGATION_DEPTH 8: asor accepts, niyikiza denies at 3i. On the grid where every token carries m, 7 of 49 cells disagree, all on the diagonal n == m, which is the difference Section 10 states. Case (d) is not in Section 10: under the -03 a child may lower "del_max_depth" (rule 5), but step 3 compares n only with DT_0's value, so the lowered value bounds nothing further down the chain.

## Failure Modes

- Checking scopes with a regex that ends in `$`: `crm.read\n` then passes as a literal under `crm.*`. Use a full match (`reject_newline_scope.json`).
- Python's `json` accepts NaN and Infinity and keeps the last of two duplicate members by default. Without hooks the verifier never reports non_finite or duplicate_member.
- Comparing derived lifetimes at step 4 reports not_narrower for `reject_child_exp_exceeds_parent.json`; rule 4 belongs to step 5 (expired).
- Using the -02 time rule (now <= exp) accepts a chain at now == exp.
- `python3 -I` drops the script's directory from `sys.path`, so `three_hop.py`, `overspend.py` and `depth_rules.py` load `verify_vectors.py` by path.
- Lab 2 is an in-process model: threads with a forced interleaving, not two real gateways on a network.

## Next Actions

- Implement step 6 (a DPoP proof checked against `cnf.jkt`), step 7 (a status list with a time to live) and the action part of step 8, then check that `valid_unknown_constraint_identical.json` denies every action with unknown_constraint.
- Score the -01 20-file set for the cases the new set does not re-mint (a chain longer than "del_max_depth", the bare and non-final wildcards, RFC 8785 number forms). It needs the -01 claim rules.
- The two "del_max_depth" points (a child that omits the claim under rule 5, and a lowered child value that step 3 never enforces) are candidates to raise with the author. Nothing has been sent.
