#!/usr/bin/env python3
"""Lab 3: feed the same depth values to the depth rules of
draft-asor-wimse-agent-delegation-chain-03 and of
draft-niyikiza-oauth-attenuating-agent-tokens-02 and record where they disagree.

asor: Section 3 (del_max_depth REQUIRED in DT_0, a positive integer; del_depth a
non-negative integer), Section 6 step 3 (DT_i.del_depth == i, n < DT_0.del_max_depth)
and step 4 rule 5 (C.del_max_depth <= P.del_max_depth). A child that omits
del_max_depth inherits its parent's value (this lab's reading; the -03 is silent).

niyikiza-02: Section 8 steps 3c, 3i, 4b4, 4d, 4e, 4f, 4g, 4m and 5, with
MAX_DELEGATION_DEPTH = 8 (the floor Section 4.3 sets).

Only the depth claims are compared: niyikiza tokens differ in type, signing key
(each child is signed by the parent's cnf key) and capability format, so no token
is shared between the two. The asor rows are also confirmed on minted Ed25519
chains with verify_vectors.py.

Usage: python3 -I depth_rules.py
"""

import hashlib
import importlib.util
import os
import platform
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("vv", os.path.join(HERE, "verify_vectors.py"))
vv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vv)

MAX_DELEGATION_DEPTH = 8
ABSENT = None


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def asor(chain):
    """chain: list of (del_depth, del_max_depth or ABSENT). Returns outcome name."""
    for i, (d, m) in enumerate(chain):
        if not _int(d) or d < 0:
            return "malformed (del_depth)"
        if i == 0 and m is ABSENT:
            return "malformed (DT_0 del_max_depth absent)"
        if m is not ABSENT and (not _int(m) or m < 1):
            return "malformed (del_max_depth not positive)"
    n = len(chain) - 1
    if chain[0][0] != 0 or any(chain[i][0] != i for i in range(1, n + 1)):
        return "depth_invalid (sequence)"
    if not n < chain[0][1]:
        return "depth_invalid (n=%d not < %d)" % (n, chain[0][1])
    eff = [chain[0][1]]
    for i in range(1, n + 1):
        eff.append(chain[i][1] if chain[i][1] is not ABSENT else eff[-1])
        if eff[i] > eff[i - 1]:
            return "not_narrower (rule 5)"
    return "accept"


def niyikiza(chain):
    d0, m0 = chain[0]
    if not (_int(d0) and d0 == 0):
        return "deny 3c"
    if m0 is ABSENT or not _int(m0) or m0 < 0 or m0 > MAX_DELEGATION_DEPTH:
        return "deny 3i"
    for i in range(1, len(chain)):
        (pd, pm), (cd, cm) = chain[i - 1], chain[i]
        if cm is ABSENT or not (_int(cd) and _int(cm)) or cd < 0 or cm < 0:
            return "deny 4b4 (DT_%d)" % i
        if cd != pd + 1:
            return "deny 4d (DT_%d)" % i
        if cd > pm:
            return "deny 4e (DT_%d depth %d > parent max %d)" % (i, cd, pm)
        if cd > MAX_DELEGATION_DEPTH:
            return "deny 4f (DT_%d)" % i
        if cm > pm:
            return "deny 4g (DT_%d)" % i
        if cd > cm:
            return "deny 4m (DT_%d)" % i
    if len(chain) != chain[-1][0] + 1:
        return "deny 5"
    return "accept"


def every(m, n):
    """n+1 tokens, every token carries del_max_depth m (niyikiza's REQUIRED shape)."""
    return [(i, m) for i in range(n + 1)]


def root_only(m, n):
    """n+1 tokens, only DT_0 carries del_max_depth (asor's minimum shape)."""
    return [(0, m)] + [(i, ABSENT) for i in range(1, n + 1)]


CASES = [
    ("leaf del_depth == root del_max_depth (m=2, n=2), all carry 2", every(2, 2)),
    ("leaf one below the bound (m=2, n=1)", every(2, 1)),
    ("leaf past the bound (m=2, n=3)", every(2, 3)),
    ("terminal root, del_max_depth 0 (m=0, n=0)", every(0, 0)),
    ("root only (m=1, n=0)", every(1, 0)),
    ("children omit del_max_depth (m=3, n=2)", root_only(3, 2)),
    ("DT_1 lowers del_max_depth to 1, DT_2 at depth 2 (root m=5)", [(0, 5), (1, 1), (2, 1)]),
    ("root del_max_depth 9 above MAX_DELEGATION_DEPTH 8 (n=1)", every(9, 1)),
    ("child sets del_max_depth = own depth, terminal (m=3, n=1)", [(0, 3), (1, 1)]),
    ("depth sequence skips 1 (0, 2)", [(0, 3), (2, 3)]),
]


def short(o):
    return "accept" if o == "accept" else "deny"


def mint_asor(chain):
    """Mint an Ed25519 asor chain with the given depth claims and run the full verifier (steps 1-5)."""
    k = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"asor-lab3:root").digest())
    hdr = {"alg": "Ed25519", "kid": "root-1", "typ": "at+jwt"}
    toks = []
    for i, (d, m) in enumerate(chain):
        p = {"iss": "https://as.example.com", "aud": "https://rs.example.com", "sub": "user:alice", "iat": 1000,
             "exp": 4600 - i, "jti": "lab3:%d" % i, "client_id": "agent-%d" % i, "cnf": {"jkt": "k%d" % i},
             "del_depth": d, "authorization_details": [{"type": "agent_delegation", "scopes": ["crm.read"]}]}
        if m is not ABSENT:
            p["del_max_depth"] = m
        if i > 0:
            p["par_hash"] = vv.par_hash(toks[-1])
        toks.append(vv.mint(hdr, p, "Ed25519", k))
    got, detail = vv.run(toks, keys={"root-1": ("Ed25519", k)}, accepted_algs=["Ed25519"], now=1500,
                         steps=(1, 2, 3, 4, 5))
    return got if got == "accept" else "%s (%s)" % (got, detail)


def main():
    print("python %s, cryptography %s" % (platform.python_version(), __import__("cryptography").__version__))
    print("MAX_DELEGATION_DEPTH (niyikiza) = %d; '-' = claim absent" % MAX_DELEGATION_DEPTH)
    print()
    print("named cases: (del_depth, del_max_depth) per token")
    disagree = 0
    for label, chain in CASES:
        a, b, full = asor(chain), niyikiza(chain), mint_asor(chain)
        diff = short(a) != short(b)
        disagree += diff
        claims = " ".join("(%d,%s)" % (d, "-" if m is ABSENT else m) for d, m in chain)
        print("  %s %s" % ("DIFF" if diff else "same", label))
        print("       tokens %s" % claims)
        print("       asor: %-42s niyikiza-02: %s" % (a, b))
        print("       asor full verifier on minted chain: %s" % full)
    print("named cases: %d of %d disagree on accept/deny" % (disagree, len(CASES)))
    print()
    print("grid: every token carries m; rows m = root del_max_depth, columns n = leaf del_depth")
    print("      cell = asor/niyikiza, A = accept, D = deny, * marks a disagreement")
    print("       " + "".join("n=%-6d" % n for n in range(0, 7)))
    cells = diffs = 0
    diff_cells = []
    for m in range(0, 7):
        row = []
        for n in range(0, 7):
            a, b = short(asor(every(m, n))), short(niyikiza(every(m, n)))
            mark = "*" if a != b else " "
            cells += 1
            if a != b:
                diffs += 1
                diff_cells.append((m, n))
            row.append("%s/%s%s    " % (a[0].upper(), b[0].upper(), mark))
        print("  m=%d  %s" % (m, "".join(row)))
    print("grid: %d of %d cells disagree: %s" % (diffs, cells, ", ".join("m=%d n=%d" % c for c in diff_cells)))
    rule = all(n == m for m, n in diff_cells)
    print("every disagreeing cell has n == m: %s" % rule)
    print()

    # self-test: wrong expectations must be caught
    print("self-test (the comparison must be able to fail):")
    st = [
        asor(every(2, 2)) != "accept",              # asor must deny leaf == bound
        niyikiza(every(2, 2)) == "accept",          # niyikiza must accept it
        niyikiza(every(2, 3)) != "accept",          # and deny one past it
        asor([(0, 3), (2, 3)]).startswith("depth_invalid"),
        mint_asor(every(2, 2)).startswith("depth_invalid"),
    ]
    mutated = every(2, 1)
    mutated[1] = (1, 3)  # child raises del_max_depth
    st.append(asor(mutated).startswith("not_narrower") and niyikiza(mutated).startswith("deny 4g"))
    print("  checks: %s" % st)
    ok = all(st) and rule
    print("self-test: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
