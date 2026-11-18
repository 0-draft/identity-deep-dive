#!/usr/bin/env python3
"""Lab 1: mint a three-hop Delegation Chain (DT_0..DT_2) with Ed25519 (alg "Ed25519",
RFC 9864) and run steps 1 to 5 of Section 6 of draft-asor-wimse-agent-delegation-chain-03
only, confirming the Table 2 outcome names and the now == exp boundary.

The verifier is verify_vectors.py in this directory (loaded by path, so `python3 -I`
works). Keys are derived from fixed seeds, and Ed25519 signing is deterministic, so
the log is reproducible.

Usage: python3 -I three_hop.py
"""

import copy
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


def key(name):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"asor-lab1:" + name.encode()).digest())


ROOT = key("root")
ROGUE = key("rogue")
KEYS = {"root-1": ("Ed25519", ROOT)}
STEPS = (1, 2, 3, 4, 5)
HEADER = {"alg": "Ed25519", "c14n": "JCS", "kid": "root-1", "typ": "at+jwt"}
SUB = "user:alice@example.com"


def detail(scopes, max_rows):
    return [{"type": "agent_delegation", "scopes": scopes,
             "constraints": [{"key": "max_rows", "max": max_rows}]}]


def base_payloads():
    jkt = lambda n: vv.b64e(hashlib.sha256(n.encode()).digest())  # stand-in thumbprints; step 6 is not run
    common = {"iss": "https://as.example.com", "aud": "https://crm.example.com", "sub": SUB, "iat": 1000}
    p0 = dict(common, client_id="planner", jti="lab1:0", exp=4600, del_depth=0, del_max_depth=3,
              cnf={"jkt": jkt("planner")}, authorization_details=detail(["crm.*", "mail.send"], 10000))
    p1 = dict(common, client_id="researcher", jti="lab1:1", exp=2800, del_depth=1,
              cnf={"jkt": jkt("researcher")}, authorization_details=detail(["crm.read", "crm.list"], 1000))
    p2 = dict(common, client_id="formatter", jti="lab1:2", exp=1900, del_depth=2,
              cnf={"jkt": jkt("formatter")}, authorization_details=detail(["crm.read"], 100))
    return [p0, p1, p2]


def build(payloads, signers=None, fix_par_hash=True):
    """Mint payloads in order, filling par_hash from the token just minted."""
    toks = []
    for i, p in enumerate(payloads):
        p = copy.deepcopy(p)
        if i > 0 and fix_par_hash:
            p["par_hash"] = vv.par_hash(toks[i - 1])
        signer = (signers or {}).get(i, ROOT)
        toks.append(vv.mint(HEADER, p, "Ed25519", signer))
    return toks


def run(label, toks, expect, now=1500, time_rule="-03"):
    got, detail = vv.run(toks, keys=KEYS, accepted_algs=["Ed25519"], now=now, time_rule=time_rule, steps=STEPS)
    ok = got == expect
    print("  %-4s %-62s expected=%-18s got=%-18s %s" % ("OK" if ok else "FAIL", label, expect, got, detail))
    return ok


def main():
    print("python %s, cryptography %s" % (platform.python_version(), __import__("cryptography").__version__))
    print("steps run: 1-5 only (no audience, no holder binding, no status list, no action)")
    pls = base_payloads()
    good = build(pls)
    print("chain: DT_0 planner {crm.*, mail.send} max_rows 10000 exp 4600 del_max_depth 3")
    print("       DT_1 researcher {crm.read, crm.list} max_rows 1000 exp 2800")
    print("       DT_2 formatter {crm.read} max_rows 100 exp 1900; iat 1000 on all; default now 1500")
    for i, t in enumerate(good):
        print("  DT_%d %d bytes, sha256(signing input)=%s" % (i, len(t), vv.par_hash(t)))
    print()
    res = []
    res.append(run("baseline", good, "accept"))

    # not_narrower: DT_2 asks for mail.* which DT_1 does not hold
    p = copy.deepcopy(pls); p[2]["authorization_details"] = detail(["crm.read", "mail.send"], 100)
    res.append(run("DT_2 adds mail.send (DT_1 lacks it), re-signed", build(p), "not_narrower"))
    p = copy.deepcopy(pls); p[1]["authorization_details"] = detail(["crm.read", "crm.list"], 20000)
    res.append(run("DT_1 max_rows 20000 > DT_0 10000, re-signed", build(p), "not_narrower"))
    p = copy.deepcopy(pls); p[1]["authorization_details"][0]["constraints"] = []
    res.append(run("DT_1 drops max_rows (absent = unbounded, rule 3)", build(p), "not_narrower"))
    p = copy.deepcopy(pls); p[2]["del_max_depth"] = 4
    res.append(run("DT_2 del_max_depth 4 > inherited 3 (rule 5)", build(p), "not_narrower"))

    # principal_altered: DT_1 names another sub, re-signed, par_hash repaired
    p = copy.deepcopy(pls); p[1]["sub"] = "user:mallory@example.com"
    res.append(run("DT_1 sub altered, re-signed, par_hash repaired", build(p), "principal_altered"))

    # par_hash_mismatch: splice DT_2 onto a different DT_1 instance
    p = copy.deepcopy(pls); p[1]["jti"] = "lab1:1-reissued"; p[1]["exp"] = 2700
    reissued = build(p)
    res.append(run("DT_2 presented with a re-issued DT_1 (new jti/exp)", [good[0], reissued[1], good[2]],
                   "par_hash_mismatch"))
    p = copy.deepcopy(pls); p[2]["par_hash"] = vv.par_hash(good[0])
    res.append(run("DT_2 par_hash points at DT_0, re-signed",
                   [good[0], good[1], vv.mint(HEADER, p[2], "Ed25519", ROOT)], "par_hash_mismatch"))

    # expired, including the boundary
    res.append(run("now = 1899 (DT_2 exp - 1)", good, "accept", now=1899))
    res.append(run("now = 1900 = DT_2 exp, -03 rule (now < exp)", good, "expired", now=1900))
    res.append(run("now = 1900 = DT_2 exp, -02 rule (now <= exp)", good, "accept", now=1900, time_rule="-02"))
    res.append(run("now = 1901, -02 rule", good, "expired", now=1901, time_rule="-02"))
    p = copy.deepcopy(pls); p[2]["exp"] = 2900
    res.append(run("DT_2 exp 2900 > DT_1 exp 2800 (rule 4), now 1500", build(p), "expired"))
    p = copy.deepcopy(pls); p[1]["nbf"] = 2000
    res.append(run("DT_1 nbf 2000 > now 1500", build(p), "expired"))

    # other step 1 and 3 names
    res.append(run("DT_1 signed by an untrusted key under kid root-1", build(pls, signers={1: ROGUE}),
                   "signature_invalid"))
    p = copy.deepcopy(pls); p[0]["del_max_depth"] = 2
    res.append(run("DT_0 del_max_depth 2: n = 2 is not < 2", build(p), "depth_invalid"))
    p = copy.deepcopy(pls); p[2]["del_depth"] = 3
    res.append(run("DT_2 del_depth 3 (skips 2)", build(p), "depth_invalid"))
    print()
    ok = all(res)
    print("lab1: %d/%d as expected -> %s" % (sum(res), len(res), "PASS" if ok else "FAIL"))

    # self-test: the harness must be able to fail. Score a widened chain as if it were
    # expected to verify; run() must report FAIL for it.
    print()
    print("self-test (a mutated chain scored as 'accept' must FAIL):")
    p = copy.deepcopy(pls); p[2]["authorization_details"] = detail(["crm.*"], 100)
    caught = not run("DT_2 widens crm.read to crm.* (deliberately wrong expectation)", build(p), "accept")
    print("self-test: %s" % ("PASS (mismatch detected)" if caught else "FAIL (mutation not detected)"))
    return 0 if ok and caught else 1


if __name__ == "__main__":
    sys.exit(main())
