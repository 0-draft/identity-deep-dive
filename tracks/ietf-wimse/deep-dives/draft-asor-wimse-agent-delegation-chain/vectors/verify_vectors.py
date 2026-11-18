#!/usr/bin/env python3
"""Independent verifier for draft-asor-wimse-agent-delegation-chain-03, Section 6.

Written from the -03 text only (no code from attenu-guard, attenu-guard-ts or
Cred). Implemented: the parse-time rules of Sections 3, 4, 4.1, 4.2 and 4.4,
steps 1 to 5 of Section 6, and the audience part of step 8. Not implemented:
step 6 (DPoP holder binding), step 7 (Token Status List) and the action part
of step 8 (scope, per-action and cumulative constraints). Results are reported
with those steps listed as not performed (Section 6.1).

Usage:
  python3 -I verify_vectors.py <vector-dir>     score the Appendix B vectors
  python3 -I verify_vectors.py --self-test <vector-dir>

Only the Python stdlib and `cryptography` (for Ed25519) are used.
"""

import base64
import decimal
import glob
import hashlib
import hmac
import json
import os
import re
import sys

MAX_SAFE = 2**53 - 1
NOT_PERFORMED = ["6 (holder binding)", "7 (status list)", "8 action check"]


class Deny(Exception):
    def __init__(self, name, detail=""):
        super().__init__(name)
        self.name = name
        self.detail = detail


# ---------------------------------------------------------------- base64url / JCS

B64URL = re.compile(r"[A-Za-z0-9_-]*")


def b64e(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def b64d(text):
    if not B64URL.fullmatch(text) or len(text) % 4 == 1:
        raise Deny("malformed", "not base64url")
    raw = base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    if b64e(raw) != text:  # non-zero trailing bits
        raise Deny("malformed", "non-canonical base64url")
    return raw


def _es_number(v):
    """ECMAScript Number::toString, as RFC 8785 Section 3.2.2.3 requires."""
    if v == 0:
        return "0"
    sign = "-" if v < 0 else ""
    t = decimal.Decimal(repr(abs(v))).normalize().as_tuple()
    digits = "".join(map(str, t.digits))
    k = len(digits)
    n = t.exponent + k
    if k <= n <= 21:
        s = digits + "0" * (n - k)
    elif 0 < n <= 21:
        s = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        s = "0." + "0" * (-n) + digits
    else:
        e = n - 1
        s = digits[0] + ("." + digits[1:] if k > 1 else "") + "e" + ("+" if e >= 0 else "-") + str(abs(e))
    return sign + s


_ESC = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}


def _jcs_str(s):
    out = []
    for ch in s:
        if ch in _ESC:
            out.append(_ESC[ch])
        elif ord(ch) < 0x20:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def jcs(v):
    """RFC 8785 serialization, returned as UTF-8 bytes."""
    return _jcs(v).encode("utf-8")


def _jcs(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, int):
        return _es_number(float(v)) if abs(v) > MAX_SAFE else str(v)
    if isinstance(v, float):
        return _es_number(v)
    if isinstance(v, str):
        return _jcs_str(v)
    if isinstance(v, list):
        return "[" + ",".join(_jcs(x) for x in v) + "]"
    if isinstance(v, dict):
        keys = sorted(v, key=lambda k: k.encode("utf-16-be", "surrogatepass"))
        return "{" + ",".join(_jcs_str(k) + ":" + _jcs(v[k]) for k in keys) + "}"
    raise TypeError(type(v))


# ---------------------------------------------------------------- JSON parse (Section 3)


def _pairs(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise Deny("duplicate_member", k)
        seen.add(k)
    return dict(pairs)


def _const(name):
    raise Deny("non_finite", name)


def _float(text):
    f = float(text)
    if f != f or f in (float("inf"), float("-inf")):
        raise Deny("non_finite", text)
    return f


def _walk(v):
    if isinstance(v, bool) or v is None:
        return
    if isinstance(v, int):
        if abs(v) > MAX_SAFE:
            raise Deny("malformed", "integer magnitude exceeds 2^53-1")
    elif isinstance(v, float):
        if v.is_integer() and abs(v) > MAX_SAFE:
            raise Deny("malformed", "integer magnitude exceeds 2^53-1")
    elif isinstance(v, str):
        if any(0xD800 <= ord(c) <= 0xDFFF for c in v):
            raise Deny("malformed", "lone surrogate")
    elif isinstance(v, list):
        for x in v:
            _walk(x)
    elif isinstance(v, dict):
        for k, x in v.items():
            _walk(k)
            _walk(x)


def parse_segment(raw):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Deny("malformed", "not UTF-8")
    try:
        obj = json.loads(text, object_pairs_hook=_pairs, parse_constant=_const, parse_float=_float)
    except ValueError as e:
        raise Deny("malformed", "JSON: %s" % e)
    _walk(obj)
    if jcs(obj) != raw:
        raise Deny("non_canonical", raw[:40].decode("utf-8", "replace"))
    if not isinstance(obj, dict):
        raise Deny("malformed", "not an object")
    return obj


# ---------------------------------------------------------------- scopes (Section 4.1)

SEG = r"[a-z][a-z0-9_-]*"
LITERAL = re.compile(SEG + r"\." + SEG + r"(?:\." + SEG + r")*")
WILDCARD = re.compile(SEG + r"(?:\." + SEG + r")*\.\*")
OPAQUE = re.compile(r"[\x21\x23-\x29\x2B-\x5B\x5D-\x7E]+")


def classify(scope):
    if LITERAL.fullmatch(scope):
        return "literal"
    if WILDCARD.fullmatch(scope):
        return "wildcard"
    if OPAQUE.fullmatch(scope):
        return "opaque"
    return None


def covers(parent, child):
    pc, cc = classify(parent), classify(child)
    if pc == "literal":
        return child == parent
    if pc == "opaque":
        return cc == "opaque" and child == parent
    if pc == "wildcard":
        return cc in ("literal", "wildcard") and child.startswith(parent[:-1])
    return False


# ---------------------------------------------------------------- claim shape

NUMBER_TYPES = ("max", "max_lifetime", "max_subtree", "min")
KNOWN_TYPES = NUMBER_TYPES + ("one_of", "not_one_of", "prefix", "rank")


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def constraint_type(c):
    """Return the type member name of a constraint object, or raise malformed."""
    if not isinstance(c, dict) or not isinstance(c.get("key"), str):
        raise Deny("malformed", "constraint without string key")
    others = sorted(set(c) - {"key"})
    if "rank" in others:
        if others != ["order", "rank"]:
            raise Deny("malformed", "rank constraint members %s" % others)
        order = c["order"]
        if (not isinstance(order, list) or len(order) < 2 or not all(isinstance(x, str) for x in order)
                or len(set(order)) != len(order)):
            raise Deny("malformed", "rank order not >=2 distinct strings")
        if not isinstance(c["rank"], str) or c["rank"] not in order:
            raise Deny("malformed", "rank not a member of order")
        return "rank"
    if len(others) != 1:
        raise Deny("malformed", "constraint members %s" % others)
    t = others[0]
    v = c[t]
    if t in NUMBER_TYPES and not _is_num(v):
        raise Deny("malformed", "%s not a number" % t)
    if t in ("one_of", "not_one_of") and not isinstance(v, list):
        raise Deny("malformed", "%s not an array" % t)
    if t == "prefix" and not isinstance(v, str):
        raise Deny("malformed", "prefix not a string")
    return t


def check_shape(i, header, p):
    def bad(msg):
        raise Deny("malformed", "DT_%d %s" % (i, msg))

    if not isinstance(header.get("alg"), str):
        bad("header alg")
    if header.get("typ") not in ("at+jwt", "application/at+jwt"):
        bad("header typ is not at+jwt")
    for name in ("iss", "jti", "client_id", "sub"):
        if not isinstance(p.get(name), str):
            bad("%s absent or not a string" % name)
    for name in ("exp", "iat"):
        if not _is_num(p.get(name)):
            bad("%s absent or not a number" % name)
    if "nbf" in p and not _is_num(p["nbf"]):
        bad("nbf not a number")
    if i == 0 and p["sub"] == "":
        bad("root sub is empty (no Principal)")
    aud = p.get("aud")
    if not (isinstance(aud, str) or (isinstance(aud, list) and aud and all(isinstance(a, str) for a in aud))):
        bad("aud absent, null, empty or not string(s)")
    cnf = p.get("cnf")
    if not isinstance(cnf, dict) or not isinstance(cnf.get("jkt"), str) or not cnf["jkt"]:
        bad("cnf carries no jkt (Section 7: JWK thumbprint)")
    if not _is_int(p.get("del_depth")) or p["del_depth"] < 0:
        bad("del_depth not a non-negative integer")
    if i == 0 and "del_max_depth" not in p:
        bad("del_max_depth absent in DT_0")
    if "del_max_depth" in p and (not _is_int(p["del_max_depth"]) or p["del_max_depth"] < 1):
        bad("del_max_depth not a positive integer")
    if i == 0 and "par_hash" in p:
        bad("par_hash present in DT_0")
    if i > 0 and not isinstance(p.get("par_hash"), str):
        bad("par_hash absent or not a string")
    ad = p.get("authorization_details")
    if not isinstance(ad, list) or len(ad) != 1:
        bad("authorization_details is not exactly one detail")
    d = ad[0]
    if not isinstance(d, dict) or d.get("type") != "agent_delegation":
        bad("detail type is not agent_delegation")
    extra = set(d) - {"type", "scopes", "constraints"}
    if extra:
        bad("detail carries unknown member(s) %s" % sorted(extra))
    scopes = d.get("scopes")
    if not isinstance(scopes, list) or not all(isinstance(s, str) for s in scopes):
        bad("scopes absent or not strings")
    for s in scopes:
        if classify(s) is None:
            bad("invalid scope %r" % s)
    cons = d.get("constraints", [])
    if not isinstance(cons, list):
        bad("constraints not an array")
    seen = set()
    for c in cons:
        t = constraint_type(c)
        if (c["key"], t) in seen:
            bad("repeated constraint (%s, %s)" % (c["key"], t))
        seen.add((c["key"], t))


def parse_chain(tokens):
    out = []
    for i, tok in enumerate(tokens):
        if not isinstance(tok, str):
            raise Deny("malformed", "DT_%d not a string" % i)
        parts = tok.split(".")
        if len(parts) != 3:
            raise Deny("malformed", "DT_%d is not three parts" % i)
        header = parse_segment(b64d(parts[0]))
        payload = parse_segment(b64d(parts[1]))
        sig = b64d(parts[2])
        check_shape(i, header, payload)
        out.append({"header": header, "payload": payload, "sig": sig,
                    "signing_input": (parts[0] + "." + parts[1]).encode("ascii")})
    return out


# ---------------------------------------------------------------- signatures (step 1)


def sign(alg, key, signing_input):
    if alg == "HS256":
        return hmac.new(key, signing_input, hashlib.sha256).digest()
    if alg == "Ed25519":
        return key.sign(signing_input)
    raise ValueError(alg)


def verify_sig(alg, key, signing_input, sig):
    if alg == "HS256":
        return hmac.compare_digest(hmac.new(key, signing_input, hashlib.sha256).digest(), sig)
    if alg == "Ed25519":
        from cryptography.exceptions import InvalidSignature
        try:
            key.public_key().verify(sig, signing_input)
            return True
        except InvalidSignature:
            return False
    return False


def mint(header, payload, alg, key):
    h = b64e(jcs(header))
    p = b64e(jcs(payload))
    si = (h + "." + p).encode("ascii")
    return h + "." + p + "." + b64e(sign(alg, key, si))


def par_hash(token):
    h, p, _ = token.split(".")
    return b64e(hashlib.sha256((h + "." + p).encode("ascii")).digest())


# ---------------------------------------------------------------- subsumption (step 4)


def _cmap(detail):
    return {(c["key"], constraint_type(c)): c for c in detail.get("constraints", [])}


def _jset(arr):
    return {jcs(x) for x in arr}


def constraint_narrower(t, c, p):
    if t in ("max", "max_lifetime", "max_subtree"):
        return c[t] <= p[t]
    if t == "min":
        return c[t] >= p[t]
    if t == "one_of":
        return _jset(c[t]) <= _jset(p[t])
    if t == "not_one_of":
        return _jset(c[t]) >= _jset(p[t])
    if t == "prefix":
        return c[t].startswith(p[t])
    if t == "rank":
        return c["order"] == p["order"] and c["order"].index(c["rank"]) <= p["order"].index(p["rank"])
    # Section 4.3: unknown type -> subsumed only if byte-identical under JCS
    return jcs(c) == jcs(p)


def subsumed(cp, pp, eff_dmd_c, eff_dmd_p):
    cd, pd = cp["authorization_details"][0], pp["authorization_details"][0]
    for s in cd["scopes"]:  # rule 1
        if not any(covers(ps, s) for ps in pd["scopes"]):
            return "scope %r not covered" % s
    cm, pm = _cmap(cd), _cmap(pd)
    for kt, pc in pm.items():
        if kt not in cm:  # rule 3
            return "constraint %s absent in child" % (kt,)
        if not constraint_narrower(kt[1], cm[kt], pc):  # rule 2
            return "constraint %s widened" % (kt,)
    if eff_dmd_c > eff_dmd_p:  # rule 5
        return "del_max_depth raised %d > %d" % (eff_dmd_c, eff_dmd_p)
    return None


# ---------------------------------------------------------------- Section 6


def verify(tokens, keys, accepted_algs, now, audience=None, time_rule="-03", steps=(1, 2, 3, 4, 5, 8)):
    """keys: {kid: (alg, key)}. Returns ("accept", notes) or raises Deny."""
    chain = parse_chain(tokens)
    n = len(chain) - 1
    if 1 in steps:
        for i, t in enumerate(chain):
            alg = t["header"]["alg"]
            if alg not in accepted_algs:
                raise Deny("signature_invalid", "DT_%d alg %s not on the accepted list" % (i, alg))
            kid = t["header"].get("kid")
            if kid not in keys:
                raise Deny("signature_invalid", "DT_%d kid %r is not a trusted key" % (i, kid))
            conf_alg, key = keys[kid]
            if alg != conf_alg:
                raise Deny("signature_invalid", "DT_%d alg %s differs from configured %s" % (i, alg, conf_alg))
            if not verify_sig(conf_alg, key, t["signing_input"], t["sig"]):
                raise Deny("signature_invalid", "DT_%d signature does not verify" % i)
    if 2 in steps:
        for i in range(1, n + 1):
            expect = b64e(hashlib.sha256(chain[i - 1]["signing_input"]).digest())
            if not hmac.compare_digest(expect.encode(), chain[i]["payload"]["par_hash"].encode()):
                raise Deny("par_hash_mismatch", "DT_%d" % i)
    pl = [t["payload"] for t in chain]
    if 3 in steps:
        if pl[0]["del_depth"] != 0:
            raise Deny("depth_invalid", "DT_0 del_depth != 0")
        for i in range(1, n + 1):
            if pl[i]["del_depth"] != i:
                raise Deny("depth_invalid", "DT_%d del_depth %r != %d" % (i, pl[i]["del_depth"], i))
        if not n < pl[0]["del_max_depth"]:
            raise Deny("depth_invalid", "n=%d not < DT_0.del_max_depth=%d" % (n, pl[0]["del_max_depth"]))
        for i in range(1, n + 1):
            if pl[i]["sub"] != pl[0]["sub"]:
                raise Deny("principal_altered", "DT_%d" % i)
    if 4 in steps:
        eff = [pl[0]["del_max_depth"]]
        for i in range(1, n + 1):
            eff.append(pl[i].get("del_max_depth", eff[i - 1]))
            why = subsumed(pl[i], pl[i - 1], eff[i], eff[i - 1])
            if why:
                raise Deny("not_narrower", "DT_%d: %s" % (i, why))
    if 5 in steps:
        for i in range(n + 1):
            if "nbf" in pl[i] and not pl[i]["nbf"] <= now:
                raise Deny("expired", "DT_%d not yet valid" % i)
            live = now < pl[i]["exp"] if time_rule == "-03" else now <= pl[i]["exp"]
            if not live:
                raise Deny("expired", "DT_%d now=%s exp=%s (%s rule)" % (i, now, pl[i]["exp"], time_rule))
        for i in range(1, n + 1):
            if pl[i]["exp"] > pl[i - 1]["exp"]:
                raise Deny("expired", "DT_%d exp %s > parent exp %s (rule 4)" % (i, pl[i]["exp"], pl[i - 1]["exp"]))
    if 8 in steps and audience is not None:
        aud = pl[n]["aud"]
        if audience not in ([aud] if isinstance(aud, str) else aud):
            raise Deny("audience_mismatch", "%r not in %r" % (audience, aud))
    return "accept"


def run(tokens, **kw):
    try:
        return verify(tokens, **kw), ""
    except Deny as d:
        return d.name, d.detail


# ---------------------------------------------------------------- vector scoring


def load_vector(path):
    with open(path, "rb") as f:
        raw = f.read()
    v = json.loads(raw)
    s = v["signer"]
    return v, raw, {"keys": {s["kid"]: (s["alg"], bytes.fromhex(s["secret_hex"]))},
                    "accepted_algs": v["verifier"]["accepted_algs"], "now": v["now"],
                    "audience": v["verifier"].get("audience")}


def score(vdir):
    files = sorted(glob.glob(os.path.join(vdir, "*.json")))
    print("vector set: %s (%d files)" % (os.path.basename(os.path.normpath(vdir)), len(files)))
    agg = hashlib.sha256()
    rows, per = [], {}
    for f in files:
        v, raw, kw = load_vector(f)
        agg.update(hashlib.sha256(raw).digest())
        expected = v.get("expect") or v.get("expect_reject_reason")
        got, detail = run(v["tokens"], **kw)
        ok = got == expected
        rows.append((os.path.basename(f), expected, got, ok, detail))
        e = per.setdefault(expected, [0, 0])
        e[0 if ok else 1] += 1
    print("aggregate sha256 over per-file sha256: %s" % agg.hexdigest())
    print()
    for name, exp, got, ok, detail in rows:
        print("%-4s %-40s expected=%-18s got=%-18s %s" % ("OK" if ok else "MISS", name, exp, got, detail))
    print()
    print("per expected outcome: name matched/mismatched")
    for k in sorted(per):
        print("  %-18s %d/%d" % (k, per[k][0], per[k][1]))
    m = sum(1 for r in rows if r[3])
    print("total: %d/%d matched" % (m, len(rows)))
    print("steps not performed: %s" % ", ".join(NOT_PERFORMED))
    return m == len(rows)


def _resign_payload(token, mutate, key):
    h, p, _ = token.split(".")
    payload = json.loads(b64d(p))
    mutate(payload)
    return mint(json.loads(b64d(h)), payload, "HS256", key)


def self_test(vdir):
    """Mutate valid_chain.json and confirm each mutation is rejected with the expected name."""
    v, _, kw = load_vector(os.path.join(vdir, "valid_chain.json"))
    t = list(v["tokens"])
    key = kw["keys"][v["signer"]["kid"]][1]
    cases = []

    def case(label, tokens, expect, **over):
        args = dict(kw)
        args.update(over)
        got, detail = run(tokens, **args)
        cases.append((label, expect, got, detail))

    case("unmodified", t, "accept")
    last = t[2][:-2] + ("AA" if not t[2].endswith("AA") else "BA")
    case("flip leaf signature bytes", t[:2] + [last], "signature_invalid")
    h, p, s = t[1].split(".")
    spaced = b64e(b64d(p).replace(b'","', b'", "', 1))
    case("insert a space in DT_1 payload (not re-signed)", [t[0], h + "." + spaced + "." + s, t[2]], "non_canonical")
    dup = b64e(b64d(p)[:-1] + b',"sub":"x"}')
    case("duplicate sub member in DT_1", [t[0], h + "." + dup + "." + s, t[2]], "duplicate_member")
    nan = b64e(b64d(p).replace(b'"exp":900', b'"exp":NaN'))
    case("exp NaN in DT_1", [t[0], h + "." + nan + "." + s, t[2]], "non_finite")

    def widen(pl):
        for c in pl["authorization_details"][0]["constraints"]:
            if c["key"] == "max_rows":
                c["max"] = 999999
    case("leaf max_rows widened, re-signed", t[:2] + [_resign_payload(t[2], widen, key)], "not_narrower")
    case("leaf scope crm.* under crm.read, re-signed",
         t[:2] + [_resign_payload(t[2], lambda pl: pl["authorization_details"][0].__setitem__("scopes", ["crm.*"]), key)],
         "not_narrower")
    case("now == leaf exp (300), -03 rule", t, "expired", now=300)
    case("now == leaf exp (300), -02 rule", t, "accept", now=300, time_rule="-02")
    case("now == leaf exp - 1 (299), -03 rule", t, "accept", now=299)
    case("unknown kid", t, "signature_invalid", keys={"other": ("HS256", key)})
    case("swap DT_0 and DT_1", [t[1], t[0], t[2]], "malformed")
    case("drop DT_1", [t[0], t[2]], "par_hash_mismatch")
    print("self-test (mutations of valid_chain.json):")
    ok = True
    for label, expect, got, detail in cases:
        good = got == expect
        ok &= good
        print("  %-4s %-50s expected=%-18s got=%-18s %s" % ("OK" if good else "FAIL", label, expect, got, detail))
    print("self-test: %s" % ("PASS" if ok else "FAIL"))
    return ok


def main(argv):
    import platform
    print("python %s, cryptography %s" % (platform.python_version(), __import__("cryptography").__version__))
    if argv[:1] == ["--self-test"]:
        return 0 if self_test(argv[1]) else 1
    good = score(argv[0])
    print()
    st = self_test(argv[0])
    return 0 if (good and st) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
