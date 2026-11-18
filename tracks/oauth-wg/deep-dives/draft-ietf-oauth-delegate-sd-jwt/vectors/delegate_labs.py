"""Hands-on labs for draft-ietf-oauth-delegate-sd-jwt-00 (dSD-JWT / dSD-JWT+KB).

Usage: python3 -I delegate_labs.py > delegate_labs.log

The draft has no worked examples, so this script mints its own tokens and checks them
with two verifiers written here from the text:

* rfc9901_verify: an SD-JWT / SD-JWT+KB verifier following RFC 9901 Sections 4, 4.3,
  7.1 and 7.3, unaware of delegation.
* dsd_verify: a prototype of draft Section 6 (with Sections 5.1.1, 5.1.3, 5.1.4).

All keys are Ed25519 derived from fixed labels, salts are derived from labels and every
timestamp is fixed, so the output is byte-for-byte reproducible (Ed25519 signatures are
deterministic; ECDSA ones are not). Exit status is 0 only if every case gives the
expected outcome and the self-test shows that the harness and the verifiers can fail.
"""
import base64
import hashlib
import json
import re
import sys

import cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

NOW = 1794960000           # 2026-11-18T00:00:00Z, the verifier's clock
ISSUED = NOW - 86400        # Issuer-signed JWT iat
DELEGATED = NOW - 3600      # KB-SD-JWT iat
PRESENTED = NOW - 60        # final KB-JWT iat
IAT_WINDOW = 300            # RFC 9901 7.3 5.e "acceptable window" (our choice)
VERIFIER = "https://shop-a.example"
NONCE = "n-0S6_WzA2Mj"


# ---------------------------------------------------------------- encoding helpers
def b64e(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def b64d(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
def cj(o): return json.dumps(o, separators=(",", ":"))
def digest(s): return b64e(hashlib.sha256(s.encode("ascii")).digest())


def key(label):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"dsd-jwt-lab-key:" + label.encode()).digest())


def jwk(priv):
    raw = priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return {"kty": "OKP", "crv": "Ed25519", "x": b64e(raw)}


def salt(label): return b64e(hashlib.sha256(b"dsd-jwt-lab-salt:" + label.encode()).digest()[:16])
def disc_obj(label, name, value): return b64e(cj([salt(label), name, value]).encode())
def disc_arr(label, value): return b64e(cj([salt(label), value]).encode())


def sign(priv, header, payload):
    si = f"{b64e(cj(header).encode())}.{b64e(cj(payload).encode())}"
    return f"{si}.{b64e(priv.sign(si.encode()))}"


class Reject(Exception):
    pass


B64URL = re.compile(r"[A-Za-z0-9_-]+")


def is_jwt(c): return c.count(".") == 2 and all(B64URL.fullmatch(p) for p in c.split("."))


def jws_verify(jws, pub_jwk, what):
    """Signature check (RFC 7515 5.2) under a JWK; returns (header, payload)."""
    if not is_jwt(jws):
        raise Reject(f"{what}: not a compact JWS")
    h, p, s = jws.split(".")
    hdr, pl = json.loads(b64d(h)), json.loads(b64d(p))
    if hdr.get("alg") != "EdDSA":  # RFC 9901 7.1 2.a: only what we deem secure; never "none"
        raise Reject(f"{what}: alg {hdr.get('alg')!r} not accepted")
    if not (isinstance(pub_jwk, dict) and pub_jwk.get("kty") == "OKP" and pub_jwk.get("crv") == "Ed25519"):
        raise Reject(f"{what}: no usable Ed25519 key to verify with")
    try:
        Ed25519PublicKey.from_public_bytes(b64d(pub_jwk["x"])).verify(b64d(s), f"{h}.{p}".encode())
    except (InvalidSignature, ValueError):
        raise Reject(f"{what}: signature invalid")
    return hdr, pl


# ---------------------------------------------------------------- RFC 9901 7.1 step 3-6
def process_sd(payload, discs, what):
    """RFC 9901 7.1 steps 3-5: resolve Disclosures, reject duplicates and unreferenced ones."""
    if payload.get("_sd_alg", "sha-256") != "sha-256":
        raise Reject(f"{what}: _sd_alg not understood")
    by_digest = {}
    for d in discs:
        if not B64URL.fullmatch(d):
            raise Reject(f"{what}: component {d[:24]!r} is not a Disclosure")
        by_digest[digest(d)] = d
    seen, used = set(), set()

    def take(dg):
        if dg in seen:
            raise Reject(f"{what}: digest seen twice (7.1 step 4)")
        seen.add(dg)
        if dg not in by_digest:
            return None
        used.add(dg)
        try:
            return json.loads(b64d(by_digest[dg]))
        except ValueError:
            raise Reject(f"{what}: Disclosure is not JSON")

    def walk(v):
        if isinstance(v, dict):
            out = {k: walk(x) for k, x in v.items() if k not in ("_sd", "_sd_alg")}
            for dg in v.get("_sd", []):
                c = take(dg)
                if c is None:
                    continue
                if not (isinstance(c, list) and len(c) == 3):
                    raise Reject(f"{what}: object Disclosure is not [salt, name, value]")
                if c[1] in ("_sd", "...") or c[1] in out:
                    raise Reject(f"{what}: bad or duplicate claim name {c[1]!r}")
                out[c[1]] = walk(c[2])
            return out
        if isinstance(v, list):
            out = []
            for x in v:
                if isinstance(x, dict) and set(x) == {"..."}:
                    c = take(x["..."])
                    if c is None:
                        continue  # 7.1 3.d: drop undisclosed array elements
                    if not (isinstance(c, list) and len(c) == 2):
                        raise Reject(f"{what}: array Disclosure is not [salt, value]")
                    out.append(walk(c[1]))
                else:
                    out.append(walk(x))
            return out
        return v

    out = walk(payload)
    if set(by_digest) - used:
        raise Reject(f"{what}: Disclosure not referenced by any digest (7.1 step 5)")
    return out


def check_validity(p, what):
    """RFC 9901 7.1 step 6 with exp/nbf."""
    if "exp" in p and NOW >= p["exp"]:
        raise Reject(f"{what}: expired")
    if "nbf" in p and NOW < p["nbf"]:
        raise Reject(f"{what}: not yet valid")


def check_kb_jwt(kb, holder_jwk, bound, what, aud=VERIFIER, nonce=NONCE):
    """RFC 9901 7.3 step 5 (b-g) for a KB-JWT bound to the string `bound`."""
    hdr, p = jws_verify(kb, holder_jwk, what)
    if hdr.get("typ") != "kb+jwt":
        raise Reject(f"{what}: typ {hdr.get('typ')!r} is not kb+jwt")
    if not isinstance(p.get("iat"), int) or abs(NOW - p["iat"]) > IAT_WINDOW:
        raise Reject(f"{what}: iat outside window")
    if p.get("aud") != aud or p.get("nonce") != nonce:
        raise Reject(f"{what}: aud/nonce mismatch")
    if p.get("sd_hash") != digest(bound):
        raise Reject(f"{what}: sd_hash mismatch")
    return p


# ---------------------------------------------------------------- RFC 9901 verifier
def rfc9901_verify(s, issuer_jwk, kb_required=True):
    """RFC 9901 Section 4 parsing, 7.1 and 7.3, with no knowledge of delegation."""
    comps = s.split("~")
    if len(comps) < 2:
        raise Reject("RFC 9901 Section 4: no '~' separator")
    jwt, discs, last = comps[0], comps[1:-1], comps[-1]
    for d in discs:  # ABNF: DISCLOSURE = BASE64URL = 1*(ALPHA / DIGIT / "-" / "_")
        if not B64URL.fullmatch(d):
            raise Reject(f"RFC 9901 Section 4 ABNF: component {d[:24]!r} between Issuer JWT and KB-JWT "
                         "is not a DISCLOSURE")
    _, pl = jws_verify(jwt, issuer_jwk, "Issuer-signed JWT")
    out = process_sd(pl, discs, "SD-JWT")
    check_validity(out, "SD-JWT")
    if kb_required:
        if last == "":
            raise Reject("RFC 9901 7.3 step 2: Key Binding required but no KB-JWT")
        check_kb_jwt(last, out.get("cnf", {}).get("jwk"), s[: len(s) - len(last)], "KB-JWT")
    return out


# ---------------------------------------------------------------- draft Section 6 verifier
def parse_chain(s):
    """Section 5.1.1: split on '~'; exactly one empty component before each KB-SD-JWT."""
    comps = s.split("~")
    if not comps or not is_jwt(comps[0]):
        raise Reject("5.1.1: first component is not an Issuer-signed JWT")
    segs, kb, i = [[comps[0], []]], None, 1
    while i < len(comps):
        c = comps[i]
        if c == "":
            if i == len(comps) - 1:
                break  # trailing '~': dSD-JWT
            if not is_jwt(comps[i + 1]):
                raise Reject("5.1.1: empty component not followed by exactly one KB-SD-JWT")
            segs.append([comps[i + 1], []])
            i += 2
            continue
        if is_jwt(c):
            if i != len(comps) - 1:
                raise Reject("5.1.1: JWT in a Disclosure position without a preceding empty component")
            kb = c  # dSD-JWT+KB
        else:
            segs[-1][1].append(c)
        i += 1
    if len(segs) < 2:
        raise Reject("Section 6 step 1: no KB-SD-JWT, so this is not a dSD-JWT")
    return segs, kb


def seg_str(seg): return seg[0] + "~" + "".join(d + "~" for d in seg[1])


def dsd_verify(s, issuer_jwk, kb_required=True, skip=()):
    """Draft Section 6. `skip` drops named checks to model a lax verifier:
    'link_hash' = steps 3.3/3.4, 'kb_sd_hash' = step 5.3."""
    segs, kb = parse_chain(s)
    form = "dSD-JWT+KB" if kb is not None else "dSD-JWT"
    _, pl0 = jws_verify(segs[0][0], issuer_jwk, "Issuer-signed JWT")           # step 2
    out0 = process_sd(pl0, segs[0][1], "SD-JWT")
    check_validity(out0, "SD-JWT")
    chain, prev, prev_cnf = [out0], segs[0], out0.get("cnf", {}).get("jwk")
    for n, seg in enumerate(segs[1:], 1):
        what, final = f"KB-SD-JWT #{n}", n == len(segs) - 1
        hdr, pl = jws_verify(seg[0], prev_cnf, what)                            # 3.1: preceding cnf
        for c, t in (("iat", int), ("aud", str), ("nonce", str)):                # 5.1.4: KB-JWT claims
            if not isinstance(pl.get(c), t):
                raise Reject(f"{what}: KB-JWT claim {c} missing")
        raw = pl.get("delegate_payload")
        if not isinstance(raw, list) or not raw:
            raise Reject(f"{what}: delegate_payload is not a non-empty array")
        if len(raw) > 1 and not all(isinstance(x, dict) and set(x) == {"..."} for x in raw):
            raise Reject(f"{what}: 5.1.4 more than one element, not all replaced with Disclosures")
        out = process_sd(pl, seg[1], what)
        dp = out["delegate_payload"]
        if len(dp) != 1 or not isinstance(dp[0], dict):                         # 3.2
            raise Reject(f"{what}: step 3.2 expects exactly one disclosed delegate_payload element, got {len(dp)}")
        delegate = dp[0]
        check_validity(delegate, what)                                          # 7.1 step 6 on the Delegate Payload
        if "link_hash" not in skip:
            if "sd_hash" in pl:                                                 # 3.3
                if pl["sd_hash"] != digest(seg_str(prev)):
                    raise Reject(f"{what}: step 3.3 sd_hash does not match the preceding token and Disclosures")
            elif pl.get("issuer_jwt_hash") != digest(prev[0]):                  # 3.4
                raise Reject(f"{what}: step 3.4 issuer_jwt_hash missing or does not match the preceding JWT")
        typ = hdr.get("typ")
        if not final and typ != "kb-sd-jwt+kb":                                 # 3.5
            raise Reject(f"{what}: step 3.5 typ {typ!r}")
        if final:                                                               # 4.2
            allowed = {"kb-sd-jwt+kb"} if form == "dSD-JWT+KB" else {"kb+sd-jwt", "kb-sd-jwt+kb"}
            if typ not in allowed:
                raise Reject(f"{what}: step 4.2 typ {typ!r} not allowed for {form}")
        if typ == "kb-sd-jwt+kb" and "cnf" not in delegate:                     # 5.1.4
            raise Reject(f"{what}: kb-sd-jwt+kb without cnf in the Delegate Payload")
        chain.append(delegate)
        prev, prev_cnf = seg, delegate.get("cnf", {}).get("jwk")
    if kb_required:                                                             # step 5
        if kb is None:
            raise Reject("step 5.1: Key Binding required but this is a dSD-JWT")
        bound = seg_str(prev) if "kb_sd_hash" not in skip else None
        hdr, p = jws_verify(kb, prev_cnf, "final KB-JWT")
        if hdr.get("typ") != "kb+jwt" or abs(NOW - p.get("iat", 0)) > IAT_WINDOW:
            raise Reject("final KB-JWT: typ or iat")
        if p.get("aud") != VERIFIER or p.get("nonce") != NONCE:
            raise Reject("final KB-JWT: aud/nonce mismatch")
        if bound is not None and p.get("sd_hash") != digest(bound):             # 5.3
            raise Reject("step 5.3: final KB-JWT sd_hash does not match the final KB-SD-JWT and Disclosures")
    return form, chain


# ---------------------------------------------------------------- token minting
ISSUER, HOLDER, HOLDER2 = key("issuer"), key("holder"), key("holder-2")
AGENT, AGENT2 = key("agent"), key("agent-2")
ISS = "https://issuer.example"


def issue(tag, holder, sd_claims, visible):
    """RFC 9901 Section 4.1/4.2: Issuer-signed JWT plus object-property Disclosures."""
    discs = [disc_obj(f"{tag}/{k}", k, v) for k, v in sd_claims.items()]
    payload = {"iss": ISS, "iat": ISSUED, "exp": ISSUED + 30 * 86400, **visible,
               "_sd": sorted(digest(d) for d in discs), "_sd_alg": "sha-256", "cnf": {"jwk": jwk(holder)}}
    return [sign(ISSUER, {"alg": "EdDSA", "typ": "example+sd-jwt"}, payload), discs]


def delegate(tag, signer, prev, payloads, link="sd_hash", typ="kb-sd-jwt+kb", aud="https://agent.example"):
    """Draft 5.1.3/5.1.4: one KB-SD-JWT; each Delegate Payload is an Array Disclosure.
    payloads: list of (visible dict, selectively disclosable dict)."""
    pay_discs, claim_discs, elems = [], [], []
    for i, (visible, sd) in enumerate(payloads):
        cds = [disc_obj(f"{tag}/{i}/{k}", k, v) for k, v in sd.items()]
        obj = {**visible, **({"_sd": sorted(digest(d) for d in cds)} if cds else {})}
        pd = disc_arr(f"{tag}/{i}/payload", obj)
        pay_discs.append(pd)
        claim_discs.append(cds)
        elems.append({"...": digest(pd)})
    linkval = digest(seg_str(prev)) if link == "sd_hash" else digest(prev[0])
    body = {"iat": DELEGATED, "aud": aud, "nonce": f"{tag}-nonce", link: linkval,
            "_sd_alg": "sha-256", "delegate_payload": elems}
    jwt = sign(signer, {"alg": "EdDSA", "typ": typ}, body)
    return jwt, pay_discs, claim_discs


def present(segs, kb=None): return "~".join(seg_str(s) for s in segs) + (kb or "")


def kb_jwt(priv, bound, aud=VERIFIER, nonce=NONCE):
    return sign(priv, {"alg": "EdDSA", "typ": "kb+jwt"},
                {"iat": PRESENTED, "aud": aud, "nonce": nonce, "sd_hash": digest(bound)})


def payment_cred(tag, holder, last4):
    return issue(tag, holder, {"given_name": "Erika", "family_name": "Mustermann", "card_last4": last4},
                 {"vct": "https://issuer.example/payment-card"})


def agent_payload(agent, merchant, max_amount):
    return ({"iss": "holder", "exp": NOW + 86400, "cnf": {"jwk": jwk(agent)}, "max_amount": max_amount},
            {"merchant": merchant, "item": "running shoes"})


def one_delegation(tag, cred, holder, agent, merchant, max_amount, link="sd_hash", typ="kb-sd-jwt+kb"):
    """Return (seg0, seg1) where seg1 discloses the single Delegate Payload and all its claims."""
    jwt, pds, cds = delegate(tag, holder, cred, [agent_payload(agent, merchant, max_amount)], link, typ)
    return cred, [jwt, pds + cds[0]]


# ---------------------------------------------------------------- harness
RESULTS = []


def case(name, fn, want):
    """Run fn; want is 'accept' or 'reject'. Records PASS/FAIL and prints one line."""
    try:
        got, detail = "accept", fn()
    except Reject as e:
        got, detail = "reject", str(e)
    ok = got == want
    RESULTS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {got} (expected {want})" + (f" -- {detail}" if detail else ""))
    return ok


def short(form_chain):
    form, chain = form_chain
    return f"{form}, {len(chain) - 1} delegation(s)"


def issuer_claims(p):
    """Which selectively disclosable Issuer claims reached the processed payload."""
    return [k for k in ("given_name", "family_name", "card_last4") if k in p]


def main():
    IJ = jwk(ISSUER)
    print("draft-ietf-oauth-delegate-sd-jwt-00 hands-on labs (RFC 9901 + draft Sections 5.1, 6, 8.1)")
    print(f"Python {sys.version.split()[0]}, cryptography {cryptography.__version__}")
    print(f"verifier clock {NOW}, Ed25519 keys from fixed labels, SHA-256 everywhere")
    print()

    # ------------------------------------------------------------ Lab 1
    print("== Lab 1: one delegation; RFC 9901 parser vs Section 6 prototype")
    cred = payment_cred("cred-a", HOLDER, "1111")
    seg0, seg1 = one_delegation("del-a", cred, HOLDER, AGENT, "shop-a", 50)
    dsd = present([seg0, seg1])
    dsd_kb = present([seg0, seg1], kb_jwt(AGENT, seg_str(seg1)))
    comps = dsd_kb.split("~")
    kinds = ["JWT" if is_jwt(c) else ("empty" if c == "" else "D") for c in comps]
    print(f"  dSD-JWT+KB components ({len(comps)}): {' ~ '.join(kinds)}")
    print(f"  dSD-JWT+KB length {len(dsd_kb)}, sha256 {digest(dsd_kb)}")
    print(f"  KB-SD-JWT header {cj(json.loads(b64d(seg1[0].split('.')[0])))}")
    print(f"  KB-SD-JWT payload {cj(json.loads(b64d(seg1[0].split('.')[1])))}")
    print(f"  Delegate Payload Disclosure {b64d(seg1[1][0]).decode()}")
    print(f"  dSD-JWT+KB: {dsd_kb}")
    plain = present([cred], kb_jwt(HOLDER, seg_str(cred)))
    case("baseline: plain SD-JWT+KB, RFC 9901 verifier", lambda: "SD-JWT+KB, " + ",".join(issuer_claims(rfc9901_verify(plain, IJ))), "accept")
    case("dSD-JWT+KB, RFC 9901 verifier", lambda: rfc9901_verify(dsd_kb, IJ), "reject")
    case("dSD-JWT (trailing ~), RFC 9901 verifier, KB not required",
         lambda: rfc9901_verify(dsd, IJ, kb_required=False), "reject")

    def no_abnf():  # what an RFC 9901 parser that skips the ABNF check runs into next
        comps = dsd_kb.split("~")
        _, pl = jws_verify(comps[0], IJ, "Issuer-signed JWT")
        return process_sd(pl, [c for c in comps[1:-1] if c and not is_jwt(c)], "SD-JWT (empty and JWT components dropped)")
    case("RFC 9901 parser that drops empty/JWT components first", no_abnf, "reject")
    case("dSD-JWT+KB, Section 6 prototype", lambda: short(dsd_verify(dsd_kb, IJ)), "accept")
    print("    processed chain:", cj(dsd_verify(dsd_kb, IJ)[1]))
    case("dSD-JWT (trailing ~), Section 6 prototype, KB not required",
         lambda: short(dsd_verify(dsd, IJ, kb_required=False)), "accept")
    case("dSD-JWT (trailing ~), Section 6 prototype, KB required (step 5.1)",
         lambda: dsd_verify(dsd, IJ), "reject")
    case("plain SD-JWT+KB, Section 6 prototype", lambda: dsd_verify(plain, IJ), "reject")
    case("two empty components before the KB-SD-JWT (5.1.1)",
         lambda: dsd_verify(dsd_kb.replace("~~", "~~~", 1), IJ), "reject")
    case("no empty component before the KB-SD-JWT (5.1.1)",
         lambda: dsd_verify(dsd_kb.replace("~~", "~", 1), IJ), "reject")
    s1b, _, _ = delegate("del-a", AGENT, seg0, [agent_payload(AGENT, "shop-a", 50)])
    bad = [s1b, seg1[1]]
    case("KB-SD-JWT signed by the agent key, not the Holder cnf (step 3.1)",
         lambda: dsd_verify(present([seg0, bad], kb_jwt(AGENT, seg_str(bad))), IJ), "reject")
    _, t1 = one_delegation("del-a", cred, HOLDER, AGENT, "shop-a", 50, typ="kb+jwt")
    case("KB-SD-JWT with typ kb+jwt (step 4.2)",
         lambda: dsd_verify(present([seg0, t1], kb_jwt(AGENT, seg_str(t1))), IJ), "reject")
    _, t2 = one_delegation("del-a", cred, HOLDER, AGENT, "shop-a", 50, typ="kb+sd-jwt")
    case("dSD-JWT+KB whose KB-SD-JWT has typ kb+sd-jwt (step 4.2)",
         lambda: dsd_verify(present([seg0, t2], kb_jwt(AGENT, seg_str(t2))), IJ), "reject")
    case("dSD-JWT whose KB-SD-JWT has typ kb+sd-jwt, KB not required",
         lambda: short(dsd_verify(present([seg0, t2]), IJ, kb_required=False)), "accept")
    case("final KB-JWT signed by the Holder key, not the agent cnf (step 5.2)",
         lambda: dsd_verify(present([seg0, seg1], kb_jwt(HOLDER, seg_str(seg1))), IJ), "reject")
    # 5.1.4: two Delegate Payloads under one signature
    jwt2, pds2, cds2 = delegate("del-multi", HOLDER, cred, [agent_payload(AGENT, "shop-a", 50),
                                                            agent_payload(AGENT, "shop-b", 80)])
    one = [jwt2, [pds2[0]] + cds2[0]]
    both = [jwt2, pds2 + cds2[0] + cds2[1]]
    case("two delegate_payload elements, one disclosed (5.1.4, step 3.2)",
         lambda: short(dsd_verify(present([cred, one], kb_jwt(AGENT, seg_str(one))), IJ)), "accept")
    case("two delegate_payload elements, both disclosed (step 3.2)",
         lambda: dsd_verify(present([cred, both], kb_jwt(AGENT, seg_str(both))), IJ), "reject")
    hid = [one[0], [pds2[0]]]
    case("Delegate Holder omits the merchant/item Disclosures (4.1)",
         lambda: "Delegate Payload keys " + ",".join(dsd_verify(present([cred, hid], kb_jwt(AGENT, seg_str(hid))), IJ)[1][1]), "accept")
    print()

    # ------------------------------------------------------------ Lab 2
    print("== Lab 2: sd_hash vs issuer_jwt_hash, drop one Issuer Disclosure")
    variants = {}
    for link in ("sd_hash", "issuer_jwt_hash"):
        s0, s1 = one_delegation(f"lab2-{link}", cred, HOLDER, AGENT, "shop-a", 50, link=link)
        variants[link] = (s0, s1)
        print(f"  {link}: KB-SD-JWT payload {cj(json.loads(b64d(s1[0].split('.')[1])))}")
    given = cred[1][0]  # the given_name Disclosure
    print(f"  dropped Issuer Disclosure: {b64d(given).decode()}")
    for link, (s0, s1) in variants.items():
        full = present([s0, s1], kb_jwt(AGENT, seg_str(s1)))
        dropped_seg0 = [s0[0], [d for d in s0[1] if d != given]]
        dropped = present([dropped_seg0, s1], kb_jwt(AGENT, seg_str(s1)))
        case(f"{link}: all Issuer Disclosures", lambda: short(dsd_verify(full, IJ)), "accept")
        case(f"{link}: given_name dropped by the Delegate Holder before its KB-JWT", lambda: ",".join(issuer_claims(dsd_verify(dropped, IJ)[1][0])),
             "reject" if link == "sd_hash" else "accept")
        stripped = full.replace(given + "~", "", 1)  # removed after the final KB-JWT was signed
        case(f"{link}: given_name stripped from the finished dSD-JWT+KB in transit",
             lambda: ",".join(issuer_claims(dsd_verify(stripped, IJ)[1][0])), "reject" if link == "sd_hash" else "accept")
        case(f"{link}: all Issuer Disclosures dropped",
             lambda: ",".join(issuer_claims(dsd_verify(present([[s0[0], []], s1], kb_jwt(AGENT, seg_str(s1))), IJ)[1][0])) or "(none)",
             "reject" if link == "sd_hash" else "accept")
        alien = disc_obj("forged", "given_name", "Mallory")
        case(f"{link}: a Disclosure the Issuer never signed added",
             lambda: dsd_verify(present([[s0[0], s0[1] + [alien]], s1], kb_jwt(AGENT, seg_str(s1))), IJ), "reject")
    print()

    # ------------------------------------------------------------ Lab 3
    print("== Lab 3: one Holder cnf key, two delegations, swap the KB-SD-JWT (Section 8.1)")
    cred_b = payment_cred("cred-b", HOLDER, "2222")
    same = json.loads(b64d(cred[0].split('.')[1]))["cnf"] == json.loads(b64d(cred_b[0].split('.')[1]))["cnf"]
    print(f"  SD-JWT A (card 1111) and SD-JWT B (card 2222) carry the same Holder cnf: {same}")
    for link in ("sd_hash", "issuer_jwt_hash"):
        a0, a1 = one_delegation(f"lab3a-{link}", cred, HOLDER, AGENT, "shop-a", 50, link=link)
        b0, b1 = one_delegation(f"lab3b-{link}", cred_b, HOLDER, AGENT, "shop-a", 5000, link=link)
        good_a = present([a0, a1], kb_jwt(AGENT, seg_str(a1)))
        good_b = present([b0, b1], kb_jwt(AGENT, seg_str(b1)))
        swap = present([a0, b1], kb_jwt(AGENT, seg_str(b1)))  # card 1111 with B's max_amount 5000
        case(f"{link}: chain A (card 1111, max 50)", lambda: short(dsd_verify(good_a, IJ)), "accept")
        case(f"{link}: chain B (card 2222, max 5000)", lambda: short(dsd_verify(good_b, IJ)), "accept")
        case(f"{link}: SD-JWT A + KB-SD-JWT B, full Section 6", lambda: dsd_verify(swap, IJ), "reject")
        case(f"{link}: SD-JWT A + KB-SD-JWT B, lax verifier (signature only, no 3.3/3.4)",
             lambda: cj([c.get(k) for c, k in zip(dsd_verify(swap, IJ, skip=("link_hash",))[1],
                                                  ("card_last4", "max_amount"))]), "accept")
        # second direction: the agent cnf is reused too, so swap the final KB-JWT instead
        kb_b = kb_jwt(AGENT, seg_str(b1))
        case(f"{link}: chain A with chain B's final KB-JWT, full Section 6",
             lambda: dsd_verify(present([a0, a1], kb_b), IJ), "reject")
        case(f"{link}: chain A with chain B's final KB-JWT, lax verifier (no 5.3)",
             lambda: short(dsd_verify(present([a0, a1], kb_b), IJ, skip=("kb_sd_hash",))), "accept")
    # control: different Holder keys; the signature check alone already catches the swap
    cred_c = payment_cred("cred-c", HOLDER2, "3333")
    a0, a1 = one_delegation("lab3a-ctl", cred, HOLDER, AGENT, "shop-a", 50)
    c0, c1 = one_delegation("lab3c-ctl", cred_c, HOLDER2, AGENT, "shop-a", 5000)
    case("control, distinct Holder keys: SD-JWT A + KB-SD-JWT C, lax verifier",
         lambda: dsd_verify(present([a0, c1], kb_jwt(AGENT, seg_str(c1))), IJ, skip=("link_hash",)), "reject")
    # same Issuer SD-JWT delegated twice with the same Disclosures: hashes are equal, swap is undetectable
    s0, x1 = one_delegation("lab3-same-1", cred, HOLDER, AGENT, "shop-a", 50)
    _, y1 = one_delegation("lab3-same-2", cred, HOLDER, AGENT2, "shop-a", 5000)
    case("same SD-JWT delegated to agent and agent-2: agent presents agent-2's KB-SD-JWT",
         lambda: dsd_verify(present([s0, y1], kb_jwt(AGENT, seg_str(y1))), IJ), "reject")
    case("same SD-JWT delegated twice, dSD-JWT without KB: anyone holding KB-SD-JWT #2 presents it",
         lambda: short(dsd_verify(present([s0, y1]), IJ, kb_required=False)), "accept")
    print()

    # ------------------------------------------------------------ self-test
    print("== self-test: the verifiers and the harness can fail")
    h, p, s = seg0[0].split(".")
    sig = bytearray(b64d(s)); sig[0] ^= 1
    flipped = dsd_kb.replace(seg0[0], f"{h}.{p}.{b64e(bytes(sig))}", 1)
    kh, kp, ks = seg1[0].split(".")
    kpl = json.loads(b64d(kp)); kpl["sd_hash"] = b64e(b"\0" * 32)
    bad_link = dsd_kb.replace(seg1[0], f"{kh}.{b64e(cj(kpl).encode())}.{ks}", 1)
    st = [case("Issuer signature bit flipped, Section 6 prototype", lambda: dsd_verify(flipped, IJ), "reject"),
          case("Issuer signature bit flipped, RFC 9901 verifier on plain SD-JWT+KB",
               lambda: rfc9901_verify(plain.replace(seg0[0], f"{h}.{p}.{b64e(bytes(sig))}", 1), IJ), "reject"),
          case("KB-SD-JWT sd_hash zeroed (signature now invalid)", lambda: dsd_verify(bad_link, IJ), "reject")]
    n = len(RESULTS)
    meta = case("harness told a tampered token should be accepted (this line must say FAIL)",
                lambda: dsd_verify(flipped, IJ), "accept")
    RESULTS.pop()  # the deliberate FAIL is the expected outcome, not a lab failure
    harness_ok = (not meta) and len(RESULTS) == n
    print(f"  harness reports a wrong expectation as FAIL: {'yes' if harness_ok else 'NO'}")
    print()
    fails = RESULTS.count(False)
    print(f"{len(RESULTS)} cases, {fails} unexpected; self-test {'OK' if all(st) and harness_ok else 'FAILED'}")
    print("ALL OK" if fails == 0 and all(st) and harness_ok else "SOMETHING FAILED")
    return 0 if fails == 0 and all(st) and harness_ok else 1


if __name__ == "__main__":
    sys.exit(main())
