#!/usr/bin/env python3
"""Lab 4: steps 6, 7 and the action part of step 8 of Section 6 of
draft-asor-wimse-agent-delegation-chain-03, on top of steps 1 to 5 and the
audience check in verify_vectors.py.

Written from the -03 text and RFC 9449 (Sections 4.3, 6.1 and 11.1, checked
against the RFC text on 2026-11-18); no code from attenu-guard,
attenu-guard-ts or Cred. The status list is an
in-memory model, not a signed status list token. What each step does here:

  6  Holder binding (Section 6 step 6, Section 7): a DPoP proof checked as
     RFC 9449 Section 4.3 lists (typ dpop+jwt, asymmetric alg on the local list,
     public jwk, signature, htm, htu without query and fragment, iat window,
     jti not seen before (Section 11.1), ath = SHA-256 of the access token)
     and the JWK SHA-256 thumbprint of the proof key equal to DT_n.cnf.jkt
     (RFC 9449 Section 6.1, RFC 7638).
  7  Revocation (Section 6 step 7, Section 8): for each DT_i that carries a
     status reference, look the index up in a cached list trusted for its time
     to live; an absent, unrefreshable or stale list is status_unknown.
  8  Action (Section 6 step 8, Section 4.2): aud, then scope coverage, then
     unknown constraint types (fail closed), then per-action constraints
     against the request only, then cumulative constraints against running
     totals supplied through a separate channel only.

The -03 leaves several things open; the choices made here are listed in
LAB_CHOICES and printed in the log. Keys come from fixed seeds and the clock is
fixed, so the log is reproducible.

Usage:
  python3 -I full_verify.py <vector-dir>           run all cases and the vector check
  python3 -I full_verify.py --break <vector-dir>   add one case with a wrong expectation;
                                                   the run must exit non-zero
"""

import copy
import hashlib
import hmac
import importlib.util
import json
import os
import platform
import sys
from urllib.parse import urlsplit, urlunsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("vv", os.path.join(HERE, "verify_vectors.py"))
vv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vv)
Deny = vv.Deny

LAB_CHOICES = [
    "A1 ath is SHA-256 of DT_n's compact serialization; the -03 does not say which token of a chain is 'the access token'.",
    "A2 iat window is |now - iat| <= 60 s, and no server nonce is issued; RFC 9449 Section 11.1 leaves the window to the server.",
    "A3 htu is compared byte-for-byte with the request URI after dropping query and fragment (RFC 9449 4.3); "
    "no RFC 3986 normalization.",
    "A4 jti replay cache: a proof jti accepted once is refused afterwards (RFC 9449 Section 11.1 makes "
    "this a server choice).",
    "A5 status reference claim is 'status': {'status_list': {'uri', 'idx'}}; the -03 names no claim. The cached list is "
    "an in-memory model (fetched_at, ttl, statuses), not a signed status list token.",
    "A6 a cached answer is trusted while now < fetched_at + ttl (same half-open form as now < exp).",
    "A7 a status reference that is not of the shape in A5, or whose idx is outside the list, is status_unknown.",
    "A8 status 'suspended' denies under the name revoked; the -03 names only revoked and unknown.",
    "A9 a per-action constraint whose key the action does not state, or states with a value of the wrong kind, "
    "denies as ceiling_exceeded; the -03 does not say what a missing quantity means.",
    "A10 the running-total channel supplies the total including A; a cumulative constraint with no total "
    "denies as ceiling_exceeded (the -03 requires the deny but assigns no Table 2 name).",
    "A11 order inside step 8: aud, scope, unknown constraint type, per-action, cumulative; the -03 says aud 'then' "
    "scope, per-action and cumulative, and does not place the unknown-type deny of Section 4.2 in that sequence.",
    "A12 cumulative totals are keyed by DT_n's jti; ancestors' max_subtree totals are not consulted (step 8 checks DT_n only).",
]

NOW = 1500
EP = "https://crm.example.com"
STATUS_URI = "https://as.example.com/status/1"
PER_ACTION = ("max", "min", "one_of", "not_one_of", "prefix", "rank")
CUMULATIVE = ("max_lifetime", "max_subtree")


def seed_key(name):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"asor-lab4:" + name.encode()).digest())


ROOT = seed_key("root")
HOLDER = {n: seed_key(n) for n in ("planner", "researcher", "formatter")}
KEYS = {"root-1": ("Ed25519", ROOT)}
HEADER = {"alg": "Ed25519", "c14n": "JCS", "kid": "root-1", "typ": "at+jwt"}


# ---------------------------------------------------------------- JWK (RFC 8037, RFC 7638)


def public_jwk(priv):
    raw = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return {"crv": "Ed25519", "kty": "OKP", "x": vv.b64e(raw)}


def jkt(jwk):
    """RFC 7638 Section 3 thumbprint over the required OKP members crv, kty, x (RFC 8037 Section 2)."""
    members = {k: jwk[k] for k in ("crv", "kty", "x")}
    return vv.b64e(hashlib.sha256(json.dumps(members, sort_keys=True, separators=(",", ":")).encode()).digest())


# ---------------------------------------------------------------- step 6: DPoP (RFC 9449)

DPOP_ALGS = ["Ed25519"]
IAT_WINDOW = 60


def make_proof(priv, htm, htu, iat, jti, ath, header_over=None, payload_over=None, drop=()):
    header = {"typ": "dpop+jwt", "alg": "Ed25519", "jwk": public_jwk(priv)}
    payload = {"jti": jti, "htm": htm, "htu": htu, "iat": iat}
    if ath is not None:
        payload["ath"] = ath
    header.update(header_over or {})
    payload.update(payload_over or {})
    for k in drop:
        payload.pop(k, None)
    h = vv.b64e(json.dumps(header, separators=(",", ":")).encode())
    p = vv.b64e(json.dumps(payload, separators=(",", ":")).encode())
    return h + "." + p + "." + vv.b64e(priv.sign((h + "." + p).encode("ascii")))


def ath_of(token):
    return vv.b64e(hashlib.sha256(token.encode("ascii")).digest())


def _hb(msg):
    raise Deny("holder_binding_failed", msg)


def _json_obj(seg):
    try:
        obj = json.loads(vv.b64d(seg).decode("utf-8"), object_pairs_hook=vv._pairs)
    except (ValueError, Deny) as e:
        _hb("proof segment does not parse: %s" % e)
    if not isinstance(obj, dict):
        _hb("proof segment is not an object")
    return obj


def check_dpop(proof, method, url, access_token, cnf_jkt, now, seen_jti):
    """RFC 9449 Section 4.3, plus the cnf binding of Sections 4.3 and 6.1."""
    if proof is None:
        _hb("no DPoP proof")
    parts = proof.split(".")
    if len(parts) != 3:
        _hb("proof is not three parts")
    header, payload = _json_obj(parts[0]), _json_obj(parts[1])
    if header.get("typ") != "dpop+jwt":
        _hb("typ %r is not dpop+jwt" % header.get("typ"))
    if header.get("alg") not in DPOP_ALGS:
        _hb("alg %r is not on the accepted asymmetric list" % header.get("alg"))
    jwk = header.get("jwk")
    if not isinstance(jwk, dict) or jwk.get("kty") != "OKP" or jwk.get("crv") != "Ed25519" or not isinstance(jwk.get("x"), str):
        _hb("jwk is not an Ed25519 public key")
    if "d" in jwk:
        _hb("jwk carries a private key")
    try:
        pub = Ed25519PublicKey.from_public_bytes(vv.b64d(jwk["x"]))
        pub.verify(vv.b64d(parts[2]), (parts[0] + "." + parts[1]).encode("ascii"))
    except (InvalidSignature, ValueError, Deny):
        _hb("proof signature does not verify under its jwk")
    for name, kind in (("jti", str), ("htm", str), ("htu", str), ("iat", (int, float))):
        if not isinstance(payload.get(name), kind) or isinstance(payload.get(name), bool):
            _hb("%s absent or of the wrong type" % name)
    if payload["htm"] != method:
        _hb("htm %s != request method %s" % (payload["htm"], method))
    u = urlsplit(url)
    target = urlunsplit((u.scheme, u.netloc, u.path, "", ""))
    if payload["htu"] != target:
        _hb("htu %s != %s" % (payload["htu"], target))
    if abs(now - payload["iat"]) > IAT_WINDOW:
        _hb("iat %s outside now %s +/- %d" % (payload["iat"], now, IAT_WINDOW))
    if payload["jti"] in seen_jti:
        _hb("jti %r already used" % payload["jti"])
    if not isinstance(payload.get("ath"), str):
        _hb("ath absent")
    if not hmac.compare_digest(payload["ath"].encode(), ath_of(access_token).encode()):
        _hb("ath is not the hash of DT_n")
    if not hmac.compare_digest(jkt(jwk).encode(), cnf_jkt.encode()):
        _hb("proof key thumbprint != DT_n.cnf.jkt")
    seen_jti.add(payload["jti"])


# ---------------------------------------------------------------- step 7: status list


def check_status(payloads, cache, fetch, now):
    for i, p in enumerate(payloads):
        if "status" not in p:
            continue  # no reference: a choice made at issuance (Section 8), not denied
        ref = p["status"]
        sl = ref.get("status_list") if isinstance(ref, dict) else None
        if (not isinstance(sl, dict) or not isinstance(sl.get("uri"), str) or not vv._is_int(sl.get("idx"))
                or sl["idx"] < 0):
            raise Deny("status_unknown", "DT_%d status reference has no usable uri/idx" % i)
        uri, idx = sl["uri"], sl["idx"]
        entry = cache.get(uri)
        if entry is None or not now < entry["fetched_at"] + entry["ttl"]:
            fresh = fetch(uri, now)
            if fresh is None:
                why = "no cached list" if entry is None else "cached list outlived ttl (fetched %d + ttl %d <= now %d)" % (
                    entry["fetched_at"], entry["ttl"], now)
                raise Deny("status_unknown", "DT_%d %s and %s cannot be fetched" % (i, why, uri))
            cache[uri] = entry = fresh
        if idx >= len(entry["statuses"]):
            raise Deny("status_unknown", "DT_%d idx %d outside a list of %d" % (i, idx, len(entry["statuses"])))
        st = entry["statuses"][idx]
        if st == "valid":
            continue
        if st in ("revoked", "suspended"):
            raise Deny("revoked", "DT_%d idx %d is %s" % (i, idx, st))
        raise Deny("status_unknown", "DT_%d idx %d has status %r" % (i, idx, st))


# ---------------------------------------------------------------- step 8: action


def _ceil(msg):
    raise Deny("ceiling_exceeded", msg)


def check_per_action(c, t, params):
    k = c["key"]
    if k not in params:
        _ceil("action states no %s for (%s, %s)" % (k, k, t))
    v = params[k]
    if t in ("max", "min"):
        if not vv._is_num(v):
            _ceil("%s=%r is not a number" % (k, v))
        if (t == "max" and v > c[t]) or (t == "min" and v < c[t]):
            _ceil("%s=%r against %s %r" % (k, v, t, c[t]))
    elif t == "one_of":
        if vv.jcs(v) not in vv._jset(c[t]):
            _ceil("%s=%r not in one_of %r" % (k, v, c[t]))
    elif t == "not_one_of":
        if vv.jcs(v) in vv._jset(c[t]):
            _ceil("%s=%r in not_one_of %r" % (k, v, c[t]))
    elif t == "prefix":
        if not isinstance(v, str) or not v.startswith(c[t]):
            _ceil("%s=%r lacks prefix %r" % (k, v, c[t]))
    elif t == "rank":
        if v not in c["order"]:
            _ceil("%s=%r not in order %r" % (k, v, c["order"]))
        if c["order"].index(v) > c["order"].index(c["rank"]):
            _ceil("%s=%r above rank %r in %r" % (k, v, c["rank"], c["order"]))


def check_action(leaf, audience, action, totals):
    aud = leaf["aud"]
    if audience not in ([aud] if isinstance(aud, str) else aud):
        raise Deny("audience_mismatch", "%r not in %r" % (audience, aud))
    d = leaf["authorization_details"][0]
    scope = action.get("scope")
    if not isinstance(scope, str) or vv.classify(scope) not in ("literal", "opaque") or not any(
            vv.covers(s, scope) for s in d["scopes"]):
        raise Deny("scope_not_granted", "%r not covered by %r" % (scope, d["scopes"]))
    cons = [(c, vv.constraint_type(c)) for c in d.get("constraints", [])]
    for c, t in cons:
        if t not in vv.KNOWN_TYPES:
            raise Deny("unknown_constraint", "(%s, %s) is not implemented; every action is denied" % (c["key"], t))
    params = action.get("params", {})
    for c, t in cons:
        if t in PER_ACTION:
            check_per_action(c, t, params)
    for c, t in cons:
        if t in CUMULATIVE:
            slot = (t, leaf["jti"], c["key"])
            if slot not in totals:
                _ceil("no running total for %s/%s/%s reaches this point (MUST deny)" % slot)
            if not vv._is_num(totals[slot]) or totals[slot] > c[t]:
                _ceil("running %s total %r against %s %r" % (c["key"], totals[slot], t, c[t]))


# ---------------------------------------------------------------- Section 6, 1 to 8


def full_verify(tokens, request, action, ctx):
    """Steps 1-5 from verify_vectors.py, then 6, 7, 8 in order; deny on the first failure."""
    try:
        vv.verify(tokens, keys=ctx["keys"], accepted_algs=["Ed25519"], now=ctx["now"], steps=(1, 2, 3, 4, 5))
        payloads = [t["payload"] for t in vv.parse_chain(tokens)]
        leaf = payloads[-1]
        check_dpop(request.get("dpop"), request["method"], request["url"], tokens[-1], leaf["cnf"]["jkt"],
                   ctx["now"], ctx["seen_jti"])
        check_status(payloads, ctx["cache"], ctx["fetch"], ctx["now"])
        check_action(leaf, ctx["audience"], action, ctx["totals"])
        return "accept", ""
    except Deny as d:
        return d.name, d.detail


# ---------------------------------------------------------------- the chain


def detail(scopes, cons):
    return [{"type": "agent_delegation", "scopes": scopes, "constraints": cons}]


def cons_for(level, extra=()):
    rows = {
        0: (10000, ["eu", "jp", "us"], ["salaries"], "/crm/", "any", 1, 100, 1000),
        1: (1000, ["eu", "jp"], ["salaries", "ssn"], "/crm/accounts/", "internal", 10, 20, 400),
        2: (100, ["eu"], ["salaries", "ssn"], "/crm/accounts/", "none", 10, 5, 100),
    }[level]
    rows_max, region, table, path, egress, batch_min, calls, spend = rows
    return [
        {"key": "max_rows", "max": rows_max},
        {"key": "batch", "min": batch_min},
        {"key": "region", "one_of": region},
        {"key": "table", "not_one_of": table},
        {"key": "path", "prefix": path},
        {"key": "egress", "rank": egress, "order": ["none", "internal", "any"]},
        {"key": "max_calls", "max_lifetime": calls},
        {"key": "max_spend", "max_subtree": spend},
    ] + list(extra)


def base_payloads():
    common = {"iss": "https://as.example.com", "aud": EP, "sub": "user:alice@example.com", "iat": 1000}
    p0 = dict(common, client_id="planner", jti="lab4:0", exp=4600, del_depth=0, del_max_depth=3,
              cnf={"jkt": jkt(public_jwk(HOLDER["planner"]))},
              status={"status_list": {"uri": STATUS_URI, "idx": 0}},
              authorization_details=detail(["crm.*", "mail.send"], cons_for(0)))
    p1 = dict(common, client_id="researcher", jti="lab4:1", exp=2800, del_depth=1,
              cnf={"jkt": jkt(public_jwk(HOLDER["researcher"]))},
              status={"status_list": {"uri": STATUS_URI, "idx": 1}},
              authorization_details=detail(["crm.read", "crm.list"], cons_for(1)))
    p2 = dict(common, client_id="formatter", jti="lab4:2", exp=1900, del_depth=2,
              cnf={"jkt": jkt(public_jwk(HOLDER["formatter"]))},
              authorization_details=detail(["crm.read"], cons_for(2)))
    return [p0, p1, p2]


def build(payloads):
    toks = []
    for i, p in enumerate(payloads):
        p = copy.deepcopy(p)
        if i > 0:
            p["par_hash"] = vv.par_hash(toks[i - 1])
        toks.append(vv.mint(HEADER, p, "Ed25519", ROOT))
    return toks


URL = EP + "/accounts/42?fields=name#top"
HTU = EP + "/accounts/42"
ACTION = {"scope": "crm.read", "params": {"max_rows": 50, "batch": 20, "region": "eu", "table": "accounts",
                                          "path": "/crm/accounts/42", "egress": "none"}}
TOTALS = {("max_lifetime", "lab4:2", "max_calls"): 3, ("max_subtree", "lab4:2", "max_spend"): 40}


def status_list(statuses, fetched_at=1400, ttl=300):
    return {"fetched_at": fetched_at, "ttl": ttl, "statuses": statuses}


def offline(uri, now):
    return None  # the status list endpoint is unreachable


def ctx(**over):
    c = {"keys": KEYS, "now": NOW, "audience": EP, "seen_jti": set(), "fetch": offline, "totals": dict(TOTALS),
         "cache": {STATUS_URI: status_list(["valid", "valid", "valid", "revoked"])}}
    c.update(over)
    return c


# ---------------------------------------------------------------- cases


class Run:
    def __init__(self):
        self.rows = []

    def case(self, step, label, expect, got, source="Table 2"):
        name, det = got
        ok = name == expect
        self.rows.append(ok)
        print("  %-4s %-4s %-58s expected=%-21s got=%-21s [%s] %s" % (
            "OK" if ok else "FAIL", step, label, expect, name, source, det))
        return ok


def main(argv):
    broken = argv[:1] == ["--break"]
    if broken:
        argv = argv[1:]
    print("python %s, cryptography %s" % (platform.python_version(), __import__("cryptography").__version__))
    print("lab choices where the -03 is silent:")
    for c in LAB_CHOICES:
        print("  " + c)
    pls = base_payloads()
    good = build(pls)
    leaf = good[-1]
    print()
    print("chain: DT_0 planner {crm.*, mail.send} status idx 0; DT_1 researcher {crm.read, crm.list} status idx 1;")
    print("       DT_2 formatter {crm.read}, no status reference; now %d; EP %s" % (NOW, EP))
    print("       DT_2 constraints: %s" % json.dumps(pls[2]["authorization_details"][0]["constraints"], separators=(",", ":")))
    for name, k in HOLDER.items():
        print("  holder %-10s jkt %s" % (name, jkt(public_jwk(k))))
    for i, t in enumerate(good):
        print("  DT_%d %d bytes, sha256(signing input)=%s" % (i, len(t), vv.par_hash(t)))
    print("request: GET %s, action %s" % (URL, json.dumps(ACTION, separators=(",", ":"))))
    print("totals channel: %s" % ", ".join("%s/%s/%s=%s" % (k + (v,)) for k, v in sorted(TOTALS.items())))
    print()

    F = HOLDER["formatter"]
    ATH = ath_of(leaf)

    def req(proof=None, method="GET", url=URL, **kw):
        if proof == "default":
            proof = make_proof(F, "GET", HTU, NOW, "p-1", ATH, **kw)
        return {"method": method, "url": url, "dpop": proof}

    R = Run()

    print("positive")
    R.case("1-8", "baseline: all eight steps", "accept", full_verify(good, req("default"), ACTION, ctx()))
    edge = {"scope": "crm.read", "params": dict(ACTION["params"], max_rows=100, batch=10)}
    at_bound = {("max_lifetime", "lab4:2", "max_calls"): 5, ("max_subtree", "lab4:2", "max_spend"): 100}
    R.case("8", "every bound met with equality (rows 100, batch 10, totals 5, 100)", "accept",
           full_verify(good, req("default"), edge, ctx(totals=at_bound)))
    c = ctx()
    full_verify(good, req("default"), ACTION, c)
    R.case("6", "second request with a new proof jti on the same context", "accept",
           full_verify(good, {"method": "GET", "url": URL, "dpop": make_proof(F, "GET", HTU, NOW, "p-2", ATH)},
                       ACTION, c))
    R.case("6", "proof iat = now - 60 (edge of the A2 window)", "accept",
           full_verify(good, {"method": "GET", "url": URL, "dpop": make_proof(F, "GET", HTU, NOW - 60, "p-3", ATH)},
                       ACTION, ctx()))
    R.case("7", "cached list at now = fetched_at + ttl - 1 (1699)", "accept",
           full_verify(good, {"method": "GET", "url": URL, "dpop": make_proof(F, "GET", HTU, 1699, "p-4", ATH)},
                       ACTION, ctx(now=1699)))
    refetch = lambda uri, now: status_list(["valid", "valid"], fetched_at=now)
    R.case("7", "stale cache (fetched 1000, ttl 300), refresh succeeds", "accept",
           full_verify(good, req("default"), ACTION,
                       ctx(cache={STATUS_URI: status_list(["revoked", "revoked"], fetched_at=1000)}, fetch=refetch)))
    print()

    print("step 6 (holder binding), one mutation per check")
    m = [
        ("no DPoP proof", req(None)),
        ("proof signed by the researcher key (DT_1 holder)",
         req(make_proof(HOLDER["researcher"], "GET", HTU, NOW, "p-1", ATH))),
        ("htm POST, request GET", req(make_proof(F, "POST", HTU, NOW, "p-1", ATH))),
        ("htu names another path", req(make_proof(F, "GET", EP + "/accounts/43", NOW, "p-1", ATH))),
        ("htu keeps the query string", req(make_proof(F, "GET", EP + "/accounts/42?fields=name", NOW, "p-1", ATH))),
        ("iat = now - 61", req(make_proof(F, "GET", HTU, NOW - 61, "p-1", ATH))),
        ("iat = now + 61", req(make_proof(F, "GET", HTU, NOW + 61, "p-1", ATH))),
        ("ath is the hash of DT_1", req(make_proof(F, "GET", HTU, NOW, "p-1", ath_of(good[1])))),
        ("ath absent", req(make_proof(F, "GET", HTU, NOW, "p-1", None))),
        ("jti absent", req(make_proof(F, "GET", HTU, NOW, "p-1", ATH, drop=("jti",)))),
        ("typ jwt", req("default", header_over={"typ": "jwt"})),
        ("alg none", req("default", header_over={"alg": "none"})),
        ("jwk carries d", req("default", header_over={"jwk": dict(public_jwk(F), d="AAAA")})),
    ]
    for label, r in m:
        R.case("6", label, "holder_binding_failed", full_verify(good, r, ACTION, ctx()))
    p = make_proof(F, "GET", HTU, NOW, "p-1", ATH)
    R.case("6", "proof signature bytes flipped", "holder_binding_failed",
           full_verify(good, req(p[:-4] + ("AAAA" if not p.endswith("AAAA") else "BAAA")), ACTION, ctx()))
    c = ctx()
    full_verify(good, req(p), ACTION, c)
    R.case("6", "the same proof replayed (jti p-1 seen)", "holder_binding_failed", full_verify(good, req(p), ACTION, c))
    print()

    print("step 7 (status list)")
    cases7 = [
        ("DT_1 idx 1 revoked", "revoked", ctx(cache={STATUS_URI: status_list(["valid", "revoked"])}), "Table 2"),
        ("DT_0 idx 0 revoked", "revoked", ctx(cache={STATUS_URI: status_list(["revoked", "valid"])}), "Table 2"),
        ("no cached list, endpoint unreachable", "status_unknown", ctx(cache={}), "Table 2"),
        ("now = fetched_at + ttl (1700), refresh fails", "status_unknown", ctx(now=1700), "Table 2"),
        ("DT_1 idx 1 outside a one-entry list", "status_unknown", ctx(cache={STATUS_URI: status_list(["valid"])}),
         "Table 2, A7"),
        ("DT_1 idx 1 suspended", "revoked", ctx(cache={STATUS_URI: status_list(["valid", "suspended"])}),
         "lab A8, draft names none"),
    ]
    for label, expect, cx, src in cases7:
        r = req(make_proof(F, "GET", HTU, cx["now"], "p-1", ATH))
        R.case("7", label, expect, full_verify(good, r, ACTION, cx), src)
    q = copy.deepcopy(pls); q[1]["status"] = {"status_list": {"uri": STATUS_URI}}
    bad_ref = build(q)
    R.case("7", "DT_1 status reference without idx", "status_unknown",
           full_verify(bad_ref, req(make_proof(F, "GET", HTU, NOW, "p-1", ath_of(bad_ref[-1]))), ACTION, ctx()),
           "lab A7, draft names none")
    print()

    print("step 8 (audience and action)")
    R.case("8", "EP is https://billing.example.com", "audience_mismatch",
           full_verify(good, req("default"), ACTION, ctx(audience="https://billing.example.com")))
    for label, scope in (("scope crm.write", "crm.write"), ("scope mail.send (held by DT_0 only)", "mail.send"),
                         ("scope crm.* (a wildcard is not an action)", "crm.*")):
        R.case("8", label, "scope_not_granted",
               full_verify(good, req("default"), dict(ACTION, scope=scope), ctx()),
               "Table 2" if scope != "crm.*" else "Table 2; wildcard action is lab")
    per = [
        ("max: max_rows 101 > 100", {"max_rows": 101}, "Table 2"),
        ("min: batch 9 < 10", {"batch": 9}, "Table 2"),
        ("one_of: region us", {"region": "us"}, "Table 2"),
        ("not_one_of: table ssn", {"table": "ssn"}, "Table 2"),
        ("prefix: path /crm/leads/7", {"path": "/crm/leads/7"}, "Table 2"),
        ("rank: egress internal above none", {"egress": "internal"}, "Table 2"),
        ("rank: egress external, not in order", {"egress": "external"}, "Table 2"),
        ("max: max_rows given as the string '50'", {"max_rows": "50"}, "lab A9"),
    ]
    for label, over, src in per:
        a = {"scope": "crm.read", "params": dict(ACTION["params"], **over)}
        R.case("8", label, "ceiling_exceeded", full_verify(good, req("default"), a, ctx()), src)
    a = {"scope": "crm.read", "params": {k: v for k, v in ACTION["params"].items() if k != "max_rows"}}
    R.case("8", "action states no max_rows", "ceiling_exceeded", full_verify(good, req("default"), a, ctx()),
           "lab A9, draft names none")
    R.case("8", "max_lifetime: running max_calls 6 > 5", "ceiling_exceeded",
           full_verify(good, req("default"), ACTION, ctx(totals=TOTALS | {("max_lifetime", "lab4:2", "max_calls"): 6})))
    R.case("8", "max_subtree: running max_spend 101 > 100", "ceiling_exceeded",
           full_verify(good, req("default"), ACTION, ctx(totals=TOTALS | {
               ("max_subtree", "lab4:2", "max_spend"): 101})))
    no_spend = {k: v for k, v in TOTALS.items() if k[2] != "max_spend"}
    R.case("8", "no running total for max_spend (MUST deny)", "ceiling_exceeded",
           full_verify(good, req("default"), ACTION, ctx(totals=no_spend)), "lab A10, draft names none")
    a = {"scope": "crm.read", "params": dict(ACTION["params"], max_spend=0, max_calls=0)}
    R.case("8", "same, with the request asserting max_spend 0 and max_calls 0", "ceiling_exceeded",
           full_verify(good, req("default"), a, ctx(totals=no_spend)), "lab A10, draft names none")
    R.case("8", "max_spend subtree total supplied for DT_1's jti only", "ceiling_exceeded",
           full_verify(good, req("default"), ACTION, ctx(totals={
               ("max_lifetime", "lab4:2", "max_calls"): 3, ("max_subtree", "lab4:1", "max_spend"): 40})),
           "lab A10/A12, draft names none")
    q = copy.deepcopy(pls)
    for i in (1, 2):
        q[i]["authorization_details"][0]["constraints"].append({"key": "quota", "units": 5})
    units = build(q)
    R.case("1-5", "DT_1 and DT_2 carry an identical {quota, units 5}: steps 1-5", "accept",
           vv.run(units, keys=KEYS, accepted_algs=["Ed25519"], now=NOW, steps=(1, 2, 3, 4, 5)))
    R.case("8", "same chain, full verification", "unknown_constraint",
           full_verify(units, req(make_proof(F, "GET", HTU, NOW, "p-1", ath_of(units[-1]))), ACTION, ctx()))
    print()

    print("order (deny on the first failure)")
    R.case("6<7", "no proof and DT_1 revoked", "holder_binding_failed",
           full_verify(good, req(None), ACTION, ctx(cache={STATUS_URI: status_list(["valid", "revoked"])})))
    R.case("7<8", "DT_1 revoked and scope crm.write", "revoked",
           full_verify(good, req("default"), dict(ACTION, scope="crm.write"),
                       ctx(cache={STATUS_URI: status_list(["valid", "revoked"])})))
    R.case("5<6", "now 1900 (DT_2 exp) and no proof", "expired", full_verify(good, req(None), ACTION, ctx(now=1900)))
    R.case("8", "unknown type and max_rows 101: unknown_constraint first (A11)", "unknown_constraint",
           full_verify(units, req(make_proof(F, "GET", HTU, NOW, "p-1", ath_of(units[-1]))),
                       {"scope": "crm.read", "params": dict(ACTION["params"], max_rows=101)}, ctx()), "lab A11")
    if broken:
        print()
        print("--break: a mutated case scored with a wrong expectation (must FAIL and exit non-zero)")
        R.case("8", "max_rows 101 scored as accept", "accept",
               full_verify(good, req("default"), {"scope": "crm.read", "params": dict(ACTION["params"], max_rows=101)},
                           ctx()))
    print()

    vec_ok = vector_check(argv[0]) if argv else False
    ok = all(R.rows)
    print()
    print("lab4: %d/%d cases as expected, vector check %s -> %s" % (
        sum(R.rows), len(R.rows), "PASS" if vec_ok else "FAIL", "PASS" if ok and vec_ok else "FAIL"))
    return 0 if ok and vec_ok else 1


def vector_check(vdir):
    """valid_unknown_constraint_identical.json: steps 1-5 + aud accept; the action part of step 8 denies."""
    path = os.path.join(vdir, "valid_unknown_constraint_identical.json")
    v, raw, kw = vv.load_vector(path)
    print("vector valid_unknown_constraint_identical.json (sha256 %s)" % hashlib.sha256(raw).hexdigest())
    print("  steps 6 and 7 not performed: the vector holds no DPoP key and its tokens carry no status reference")
    got = vv.run(v["tokens"], **kw)
    res = [got[0] == "accept"]
    print("  %-4s steps 1-5 + aud, as the vector expects            got=%s %s" % (
        "OK" if res[-1] else "FAIL", got[0], got[1]))
    leaf = [t["payload"] for t in vv.parse_chain(v["tokens"])][-1]
    action = {"scope": "crm.read", "params": {"max_rows": 10, "egress": "none", "max_spend": 5}}
    totals = {("max_lifetime", "chain:n2", "max_calls"): 1, ("max_subtree", "chain:n2", "max_spend"): 5}
    print("  sample action %s" % json.dumps(action, separators=(",", ":")))
    print("  totals channel max_calls=1 (bound 2), max_spend subtree=5 (bound 100)")
    try:
        check_action(leaf, kw["audience"], action, totals)
        got = ("accept", "")
    except Deny as d:
        got = (d.name, d.detail)
    res.append(got[0] == "unknown_constraint")
    print("  %-4s step 8 action on DT_2                              got=%s %s" % (
        "OK" if res[-1] else "FAIL", got[0], got[1]))
    ctl = copy.deepcopy(leaf)
    ctl["authorization_details"][0]["constraints"] = [
        c for c in ctl["authorization_details"][0]["constraints"] if c["key"] != "quota"]
    try:
        check_action(ctl, kw["audience"], action, totals)
        got = ("accept", "")
    except Deny as d:
        got = (d.name, d.detail)
    res.append(got[0] == "accept")
    print("  %-4s control: same action, DT_2 payload with quota removed in memory (not re-signed)  got=%s %s" % (
        "OK" if res[-1] else "FAIL", got[0], got[1]))
    return all(res)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
