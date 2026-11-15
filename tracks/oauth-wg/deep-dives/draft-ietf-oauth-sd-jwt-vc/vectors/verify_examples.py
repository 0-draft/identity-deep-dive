"""Verify the SD-JWT VC examples in a draft-ietf-oauth-sd-jwt-vc .txt file.

Usage: python3 -I verify_examples.py draft-ietf-oauth-sd-jwt-vc-26.txt 7 8 10 24 26

For each figure it checks the Issuer signature (ES256, keys taken from Figure 14),
that every Disclosure digest appears in the payload or in another Disclosure, and,
when a KB-JWT is attached, its signature under the cnf key and its sd_hash.
"""
import sys, re, json, base64, hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


def b64d(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
def b64e(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


lines = [l for l in open(sys.argv[1], encoding="utf-8").read().split("\n")
         if not re.match(r"^(Terbu, et al\.|Internet-Draft  )", l) and "\f" not in l]
TOKEN = re.compile(r"\s*[A-Za-z0-9_\-.~]+\s*")


def figure_blob(n):
    """The compact serialization printed just above the caption of Figure n."""
    j = next(i for i, l in enumerate(lines) if f"Figure {n}: " in l) - 1
    while not lines[j].strip():
        j -= 1
    out = []
    while True:
        if lines[j].strip() and TOKEN.fullmatch(lines[j]):
            out.append(lines[j].strip()); j -= 1; continue
        k = j  # a page break leaves blank lines inside the blob
        while not lines[k].strip():
            k -= 1
        if k != j and TOKEN.fullmatch(lines[k]) and len(lines[k].strip()) > 40:
            j = k; continue
        return "".join(reversed(out))


def ec_key(j):
    return ec.EllipticCurvePublicNumbers(int.from_bytes(b64d(j["x"]), "big"),
                                         int.from_bytes(b64d(j["y"]), "big"), ec.SECP256R1()).public_key()


def es256_ok(jwk, jws):
    h, p, s = jws.split(".")
    sig = b64d(s)
    try:
        ec_key(jwk).verify(encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big")),
                           f"{h}.{p}".encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def digests(obj, acc):
    if isinstance(obj, dict):
        acc.update(obj.get("_sd", []))
        for k, v in obj.items():
            if k != "_sd": digests(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, dict) and set(v) == {"..."}: acc.add(v["..."])
            else: digests(v, acc)


text = "\n".join(lines)
keys = {m.group(1): {"x": m.group(2), "y": m.group(3)} for m in re.finditer(
    r'"kid":\s*"([^"]+)",\s*"kty": "EC", "crv": "P-256",\s*"x":\s*"([^"]+)",\s*"y":\s*"([^"]+)"', text)}
print("issuer keys (Figure 14):", ", ".join(keys))
def check(blob):
    """Return (ok, description) for one compact SD-JWT (+KB) string."""
    parts = blob.split("~")
    jwt, discs, kb = parts[0], [d for d in parts[1:-1] if d], parts[-1]
    hdr, pl = json.loads(b64d(jwt.split(".")[0])), json.loads(b64d(jwt.split(".")[1]))
    cands = [hdr["kid"]] if hdr.get("kid") in keys else list(keys)
    good = [k for k in cands if es256_ok(keys[k], jwt)]
    acc = set(); digests(pl, acc)
    for d in discs: digests(json.loads(b64d(d)), acc)
    missing = [d for d in discs if b64e(hashlib.sha256(d.encode()).digest()) not in acc]
    line = (f"typ={hdr.get('typ')} kid={hdr.get('kid', '-')} issuer-sig={'OK (' + good[0] + ')' if good else 'FAIL'} "
            f"disclosures={len(discs)} digests-not-found={len(missing)}")
    ok = bool(good) and not missing
    if kb:
        kbp = json.loads(b64d(kb.split(".")[1]))
        kb_ok = es256_ok(pl["cnf"]["jwk"], kb)
        sd_ok = b64e(hashlib.sha256(blob[:blob.rindex("~") + 1].encode()).digest()) == kbp["sd_hash"]
        line += f" | KB-JWT sig={'OK' if kb_ok else 'FAIL'} sd_hash={'OK' if sd_ok else 'FAIL'} iat={kbp.get('iat')}"
        ok = ok and kb_ok and sd_ok
    return ok, line


all_ok = True
for n in map(int, sys.argv[2:]):
    ok, line = check(figure_blob(n))
    all_ok &= ok
    print(f"Figure {n}: {line}")
print("ALL OK" if all_ok else "SOMETHING FAILED")

# Self-test: the checks must fail on altered input (Figure 8 has a KB-JWT and Disclosures).
blob = figure_blob(8)
parts = blob.split("~")
d0 = json.loads(b64d(parts[1])); d0[2] = str(d0[2]) + "x"
mut_disc = "~".join([parts[0], b64e(json.dumps(d0).encode())] + parts[2:])
h, p, s = parts[0].split(".")
sig = bytearray(b64d(s)); sig[-1] ^= 1
mut_sig = "~".join([f"{h}.{p}.{b64e(bytes(sig))}"] + parts[1:])
kh, kp, ks = parts[-1].split(".")
kpl = json.loads(b64d(kp)); kpl["sd_hash"] = b64e(b"\0" * 32)
mut_kb = "~".join(parts[:-1] + [f"{kh}.{b64e(json.dumps(kpl).encode())}.{ks}"])
print("self-test on Figure 8:")
selftest_ok = True
for name, m in (("Disclosure value changed", mut_disc), ("Issuer signature bit flipped", mut_sig), ("KB-JWT sd_hash replaced", mut_kb)):
    ok, line = check(m)
    selftest_ok &= not ok
    print(f"  {name}: {'rejected' if not ok else 'NOT REJECTED'} ({line})")
sys.exit(0 if all_ok and selftest_ok else 1)
