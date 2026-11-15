"""Re-run the issue #419 checks against the Zenodo v4 set (P-04 fix, N-09b).

Usage: python3 -I verify_419_v4.py verify_419.py s01-vector-set-v4-publication-2026-11-13.md
The second file is the v4 record (DOI 10.5281/zenodo.24203971). Reuses verify_419.py;
only CONNECT `@authority` is computed differently (RFC 9421 Section 2.2.3, default port omitted).
"""
import sys, re, hashlib, platform, importlib.util
import cryptography
spec = importlib.util.spec_from_file_location("v", sys.argv[1]); v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
raw = open(sys.argv[2], "rb").read(); md = raw.decode("utf-8")
print(f"python {platform.python_version()}, cryptography {cryptography.__version__}; v4 file md5 {hashlib.md5(raw).hexdigest()}")

# 1. every literal signature in v4 vs the values the 11 Nov script used
lit = {}
for sec in re.split(r"\n### |\n- \*\*", md):
    m = re.search(r"<!-- id:([PN]-\d+b?) -->", sec)
    s = re.findall(r"sig\d=:([A-Za-z0-9+/=]+):", sec)
    if m and s: lit[m.group(1)] = s
print("== literal signatures, v4 vs 11 Nov script")
for vid, s in sorted(lit.items()):
    old = [v.SIG.get(vid)] if vid != "P-06" else [v.SIG["P-06-sig1"], v.SIG["P-06-sig2"]]
    print(f"  {vid}: {'same' if s == old else 'CHANGED'}")
for w in ("WIT_A", "WIT_B", "WIT_C"):
    print(f"  {w} in v4: {getattr(v, w) in md}")

orig_cv = v.component_value
def rfc9421_cv(msg, name, params):
    # RFC 9421 Section 2.2.3: lowercase host, omit default port (443, as the v4 author reads it)
    if name == "@authority" and not dict(params).get("req") and msg.method == "CONNECT":
        a = msg.target.lower()
        return a[:-4] if a.endswith(":443") else a
    if name == "@authority" and dict(params).get("req") and msg.request is not None and msg.request.method == "CONNECT":
        a = msg.request.target.lower(); return a[:-4] if a.endswith(":443") else a
    return orig_cv(msg, name, params)

OLD_P04, NEW_P04 = v.SIG["P-04"], lit["P-04"][0]
def p04(sig): return v.req("CONNECT", "svcb.example.com:443", "svcb.example.com:443", v.WIT_A, v.SI["P-04"], f"sig1=:{sig}:")
now = v.T0 + 60
print("\n== P-04")
for rule, cv in (("draft-08 reading (host:port)", orig_cv), ("RFC 9421 2.2.3 (default port omitted)", rfc9421_cv)):
    v.component_value = cv
    for lbl, sig in (("old sig", OLD_P04), ("v4 sig", NEW_P04)):
        ok, f = v.verify(p04(sig), now); print(f"  {rule:40} {lbl}: accept={ok} {f}")
v.component_value = rfc9421_cv
print("  base line:", [l for l in v.signature_base(p04(NEW_P04), *v.first_sig(p04(NEW_P04))[1:]).split("\n") if l.startswith('"@authority"')])

print("\n== N-02 on v4 P-04 (cover @path too, re-signed with svcA)")
m = p04(NEW_P04)
_, it, pa = v.first_sig(m)
n02 = v.resign(m, "svcA", items=it[:2] + [("@path", [])] + it[2:])
ok, f = v.verify(n02, now); print(f"  accept={ok} {f}  (expected reject)")

print("\n== N-09b (P-01 bytes, verify at T0+300 and T0+301)")
for t, exp in ((300, True), (301, False)):
    ok, f = v.verify(v.P01(), v.T0 + t); print(f"  T0+{t}: accept={ok} expected={exp} {'MATCH' if ok == exp else 'MISMATCH'} {f}")
