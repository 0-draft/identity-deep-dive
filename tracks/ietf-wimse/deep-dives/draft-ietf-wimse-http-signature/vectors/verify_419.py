#!/usr/bin/env python3
"""Independent re-run of the test vectors in ietf-wg-wimse/draft-ietf-wimse-s2s-protocol#419
against draft-ietf-wimse-http-signature-08 (RFC 9421 profile).

Usage: python3 -I wimse419_verify.py [DRAFT_INCLUDES_DIR]

Everything below is written from the issue text (+ the 2026-11-07 regeneration comment) and the
-08 draft text. Nothing is imported from the vector author's code.
"""
import base64, hashlib, json, re, sys, os

from cryptography.hazmat.primitives.asymmetric import ed25519, ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

T0 = 1795000000
NOW = T0 + 60
TAG = "wimse-workload-to-workload"
ISSUER = "https://example.com/issuer"
TRUSTED_AUD = {"https://svcb.example.com/gimme-ice-cream", "https://svcb.example.com/inventory/cones",
               "https://svcb.example.com/status", "https://svcb.example.com"}
ACCEPTABLE_ALGS = {"Ed25519", "EdDSA", "ES256"}  # local policy (draft 3.1)

# --------------------------------------------------------------------------------------------
# base64url / keys
def b64u_dec(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
def b64u_enc(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

KEYS = {  # from the issue's key-material section (test-only, published by the vector author)
    "issuer": {"alg":"Ed25519","crv":"Ed25519","kid":"issuer-key","kty":"OKP","x":"QH_Zu0pnwyO8xdFQm9upOUFAbpb4nhMrGc29L3uJXDA","d":"4nRAPQQyr8cUgAtCESLc4ZIGIxZT9-guqxcc3wV-2NI"},
    "svcA": {"alg":"Ed25519","crv":"Ed25519","kid":"vec-a-key","kty":"OKP","x":"O3OfVmPJ3peYhdDrMweNIiBOQU6JZCNcYMK2kjV0i3Y","d":"F8BhX5poMswcVwTgEMGETOhdN72PaxIiwuGYWrzSUvk"},
    "svcB": {"alg":"Ed25519","crv":"Ed25519","kid":"vec-b-key","kty":"OKP","x":"4jVAzgEPO5n-6jujSiyQME5t-tIzZApbhR5cTPoedII","d":"4MaIKp1h5mkTS7ZSawz6QYN6FYA_rOYBPDfGEZCpPDg"},
    "svcC": {"alg":"ES256","crv":"P-256","kid":"vec-c-key","kty":"EC","x":"jZjfUBQgD1l9R_lm4nzo1rP82pGVDBxHD6YmOo_xoCo","y":"CBGv9b8hB-l0mov9rlu223g-vNE_SquCC2IhPi2IweE","d":"X94ti7AkOiC4JcxdbSmLkwWEzyEU4wMqBX_9LHfXQaU"},
    "other": {"alg":"Ed25519","crv":"Ed25519","kid":"other-key","kty":"OKP","x":"Lo6grJBjN252d2huS1-ckJIql2FZR2vrTOF2qKRBTm4","d":"KL4_B1CdV7qwZkVYvyK0I5SrsEzv6yb1p1PNAfbC7LY"},
}

def pub_from_jwk(j):
    if j["kty"] == "OKP" and j["crv"] == "Ed25519":
        return ed25519.Ed25519PublicKey.from_public_bytes(b64u_dec(j["x"]))
    if j["kty"] == "EC" and j["crv"] == "P-256":
        return ec.EllipticCurvePublicNumbers(int.from_bytes(b64u_dec(j["x"]), "big"),
                                             int.from_bytes(b64u_dec(j["y"]), "big"), ec.SECP256R1()).public_key()
    raise ValueError("unsupported jwk")

def priv_from_jwk(j):
    if j["kty"] == "OKP":
        return ed25519.Ed25519PrivateKey.from_private_bytes(b64u_dec(j["d"]))
    return ec.derive_private_key(int.from_bytes(b64u_dec(j["d"]), "big"), ec.SECP256R1())

def sign_raw(jwk, data):
    k = priv_from_jwk(jwk)
    if jwk["kty"] == "OKP":
        return k.sign(data)
    der = k.sign(data, ec.ECDSA(hashes.SHA256(), deterministic_signing=True))  # RFC 6979
    r, s = decode_dss_signature(der)
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")

def verify_raw(alg, jwk, data, sig):
    pub = pub_from_jwk(jwk)
    try:
        if alg in ("Ed25519", "EdDSA"):
            if not isinstance(pub, ed25519.Ed25519PublicKey): return False
            pub.verify(sig, data); return True
        if alg == "ES256":
            if not isinstance(pub, ec.EllipticCurvePublicKey) or len(sig) != 64: return False
            pub.verify(encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big")),
                       data, ec.ECDSA(hashes.SHA256())); return True
    except InvalidSignature:
        return False
    return False

def pubjwk(name):
    return {k: v for k, v in KEYS[name].items() if k != "d"}

# --------------------------------------------------------------------------------------------
# RFC 8941 structured fields (only what RFC 9421 Signature-Input / Signature / Accept-Signature need)
class Token(str): pass

class SFParser:
    def __init__(self, s): self.s, self.i = s, 0
    def ws(self):
        while self.i < len(self.s) and self.s[self.i] in " \t": self.i += 1
    def key(self):
        m = re.compile(r"[a-z*][a-z0-9_\-.*]*").match(self.s, self.i)
        if not m: raise ValueError(f"bad key at {self.i}: {self.s[self.i:self.i+20]!r}")
        self.i = m.end(); return m.group()
    def bare(self):
        c = self.s[self.i]
        if c == '"':
            self.i += 1; out = []
            while True:
                c = self.s[self.i]; self.i += 1
                if c == "\\": out.append(self.s[self.i]); self.i += 1
                elif c == '"': return "".join(out)
                else: out.append(c)
        if c == ":":
            j = self.s.index(":", self.i + 1); v = base64.b64decode(self.s[self.i+1:j]); self.i = j + 1; return v
        if c == "?":
            v = self.s[self.i+1] == "1"; self.i += 2; return v
        m = re.compile(r"-?[0-9]+").match(self.s, self.i)
        if m: self.i = m.end(); return int(m.group())
        m = re.compile(r"[A-Za-z*][A-Za-z0-9:/!#$%&'*+\-.^_`|~]*").match(self.s, self.i)
        if m: self.i = m.end(); return Token(m.group())
        raise ValueError(f"bad bare item at {self.i}")
    def params(self):
        p = []
        while self.i < len(self.s) and self.s[self.i] == ";":
            self.i += 1; self.ws(); k = self.key(); v = True
            if self.i < len(self.s) and self.s[self.i] == "=": self.i += 1; v = self.bare()
            p.append((k, v))
        return p
    def item_or_inner(self):
        if self.s[self.i] == "(":
            self.i += 1; items = []
            while True:
                self.ws()
                if self.s[self.i] == ")": self.i += 1; break
                v = self.bare(); items.append((v, self.params()))
            return ("inner", items, self.params())
        v = self.bare(); return ("item", v, self.params())
    def dictionary(self):
        out = []
        while self.i < len(self.s):
            self.ws(); k = self.key()
            if self.i < len(self.s) and self.s[self.i] == "=": self.i += 1; m = self.item_or_inner()
            else: m = ("item", True, self.params())
            out.append((k, m)); self.ws()
            if self.i < len(self.s):
                if self.s[self.i] != ",": raise ValueError("expected ,")
                self.i += 1
        return out

def ser_bare(v):
    if v is True: return "?1"
    if v is False: return "?0"
    if isinstance(v, Token): return str(v)
    if isinstance(v, int): return str(v)
    if isinstance(v, bytes): return ":" + base64.b64encode(v).decode() + ":"
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'

def ser_params(p):
    return "".join(";" + k + ("" if v is True else "=" + ser_bare(v)) for k, v in p)

def ser_inner(items, params):
    return "(" + " ".join(ser_bare(v) + ser_params(ip) for v, ip in items) + ")" + ser_params(params)

# --------------------------------------------------------------------------------------------
# HTTP message model
class Msg:
    def __init__(self, kind, headers, body=b"", method=None, target=None, status=None, request=None):
        self.kind, self.headers, self.body = kind, list(headers), body
        self.method, self.target, self.status, self.request = method, target, status, request
    def hget(self, name):
        vals = [v.strip() for n, v in self.headers if n.lower() == name.lower()]
        return ", ".join(vals) if vals else None
    def hset(self, name, value):
        self.headers = [(n, v) for n, v in self.headers if n.lower() != name.lower()]
        if value is not None: self.headers.append((name, value))
    def copy(self):
        return Msg(self.kind, self.headers, self.body, self.method, self.target, self.status, self.request)

def parse_http(text, body=b""):
    lines = text.strip("\n").split("\n")
    first, hdrs = lines[0], []
    for ln in lines[1:]:
        if not ln.strip(): break
        n, v = ln.split(":", 1); hdrs.append((n.strip(), v.strip()))
    if first.startswith("HTTP/"):
        return Msg("response", hdrs, body, status=int(first.split()[1]))
    m, t, _ = first.split(" ")
    return Msg("request", hdrs, body, method=m, target=t)

def split_target(msg):
    t = msg.target
    if msg.method == "CONNECT":  # authority-form: target URI path is empty -> "/" (RFC 9421 2.2.6), no query
        return "/", None
    if "?" in t: p, q = t.split("?", 1); return p, q
    return t, None

def component_value(msg, name, params):
    pd = dict(params)
    if pd.get("req"):
        if msg.request is None: raise KeyError("no related request for ;req")
        msg = msg.request
    if name == "@method": return msg.method
    if name == "@path": return split_target(msg)[0]
    if name == "@query":
        q = split_target(msg)[1]; return "?" + (q or "")
    if name == "@authority":
        if msg.method == "CONNECT": return msg.target.lower()  # draft: host and port of the CONNECT target
        return msg.hget("host").lower()
    if name == "@status":
        if msg.kind != "response": raise KeyError("@status on request")
        return str(msg.status)
    if name.startswith("@"): raise KeyError(f"unsupported derived component {name}")
    v = msg.hget(name)
    if v is None: raise KeyError(f"covered header {name} absent")
    return v

def signature_base(msg, items, params):
    lines = []
    for name, ip in items:
        lines.append(f"{ser_bare(name)}{ser_params(ip)}: {component_value(msg, name, ip)}")
    lines.append(f'"@signature-params": {ser_inner(items, params)}')
    return "\n".join(lines)

# --------------------------------------------------------------------------------------------
# WIT
def make_jwt(payload, header=None, key="issuer"):
    header = header or {"alg": "Ed25519", "kid": "issuer-key", "typ": "wit+jwt"}
    h = b64u_enc(json.dumps(header, separators=(",", ":"), sort_keys=True).encode())
    p = b64u_enc(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    return h + "." + p + "." + b64u_enc(sign_raw(KEYS[key], (h + "." + p).encode()))

def validate_wit(wit, now):
    """My reading of workload-creds 5.1.4 essentials: typ, issuer signature, iss, sub, exp, cnf.jwk(+alg)."""
    errs = []
    try:
        h_b, p_b, s_b = wit.split(".")
        hdr, pl = json.loads(b64u_dec(h_b)), json.loads(b64u_dec(p_b))
    except Exception as e:
        return None, [f"WIT malformed: {e}"]
    if hdr.get("typ") != "wit+jwt": errs.append("WIT typ != wit+jwt")
    if hdr.get("alg") not in ("Ed25519", "EdDSA"): errs.append(f"WIT alg {hdr.get('alg')} not issuer alg")
    elif not verify_raw(hdr["alg"], pubjwk("issuer"), (h_b + "." + p_b).encode(), b64u_dec(s_b)):
        errs.append("WIT issuer signature invalid")
    if pl.get("iss") != ISSUER: errs.append("WIT iss not trusted")
    if not pl.get("sub"): errs.append("WIT sub missing")
    if not isinstance(pl.get("exp"), int) or not now < pl["exp"]: errs.append(f"WIT expired (exp={pl.get('exp')}, now={now})")
    if isinstance(pl.get("iat"), int) and pl["iat"] > now: errs.append("WIT iat in future")
    jwk = (pl.get("cnf") or {}).get("jwk")
    if not jwk: errs.append("WIT cnf.jwk missing")
    elif "alg" not in jwk: errs.append("WIT cnf.jwk.alg missing")
    elif "d" in jwk: errs.append("WIT cnf.jwk contains private key")
    return pl, errs

# --------------------------------------------------------------------------------------------
# signing helper for building negative variants (same keys, deterministic -> reproducible)
def sign_msg(msg, label, items, params, keyname, existing=None):
    base = signature_base(msg, items, params)
    sig = sign_raw(KEYS[keyname], base.encode())
    si = (existing[0] + ", " if existing else "") + f"{label}={ser_inner(items, params)}"
    sv = (existing[1] + ", " if existing else "") + f"{label}=:{base64.b64encode(sig).decode()}:"
    msg.hset("Signature-Input", si); msg.hset("Signature", sv)
    return msg

def C(*names):  # component list helper: "@path;req" -> ("@path", [("req", True)])
    out = []
    for n in names:
        if n.endswith(";req"): out.append((n[:-4], [("req", True)]))
        else: out.append((n, []))
    return out

# --------------------------------------------------------------------------------------------
# verifier
REQ_HEADERS_IF_PRESENT = ["content-type", "content-digest", "authorization", "txn-token", "workload-identity-token"]

class Policy:
    def __init__(self, reject_keyid_alg=True, enforce_sender_coverage_musts=True, select="tag"):
        self.reject_keyid_alg = reject_keyid_alg  # draft only says the params "MUST NOT be used" (sender side)
        self.enforce_sender_coverage_musts = enforce_sender_coverage_musts  # "MUST be signed" / CONNECT MUST NOT
        self.select = select  # "tag" (draft) or "first-label" (N-22 strawman)

def check_digest(msg):
    errs = []
    if not msg.body: return errs
    cd = msg.hget("content-digest")
    if cd is None: return ["body present but Content-Digest absent (S3 / RFC 9530)"]
    try:
        d = SFParser(cd).dictionary()
    except Exception:
        return ["Content-Digest malformed"]
    supported = {"sha-256": hashlib.sha256, "sha-512": hashlib.sha512}
    seen = False
    for alg, (_, v, _) in d:
        if alg in supported:
            seen = True
            if supported[alg](msg.body).digest() != v: errs.append(f"Content-Digest {alg} mismatch with received body")
    if not seen: errs.append("Content-Digest has no supported algorithm")
    return errs

def verify(msg, now, policy=None, req_nonce=None):
    """Returns (accept, [failure reasons]). Error surface for a request failure is always 400 + wimse-signature-invalid."""
    policy = policy or Policy()
    fails = []
    si_raw, sv_raw = msg.hget("signature-input"), msg.hget("signature")
    if si_raw is None or sv_raw is None:
        return False, ["no Signature/Signature-Input"]
    si = SFParser(si_raw).dictionary(); sv = dict((k, m[1]) for k, m in SFParser(sv_raw).dictionary())
    # --- select WIMSE signature (S3: by tag, never by label; >1 tag -> reject)
    if policy.select == "tag":
        cands = [(k, m) for k, m in si if dict(m[2]).get("tag") == TAG]
        if len(cands) == 0: return False, ["no signature with tag wimse-workload-to-workload (S3)"]
        if len(cands) > 1: return False, [f"{len(cands)} signatures carry the WIMSE tag -> MUST reject (S3)"]
        label, (_, items, params) = cands[0]
    else:
        label, (_, items, params) = si[0]
    pd = dict(params)
    names = [(n, tuple(sorted(dict(ip).items()))) for n, ip in items]
    def covered(n, req=False): return (n, (("req", True),) if req else ()) in names
    is_req = msg.kind == "request"
    connect = (msg.method if is_req else (msg.request.method if msg.request else None)) == "CONNECT"
    # --- WIT first (S3: validate WIT before the HTTP message signature)
    wit = msg.hget("workload-identity-token")
    if wit is None: return False, ["Workload-Identity-Token header absent"]
    wit_pl, wit_errs = validate_wit(wit, now)
    fails += wit_errs
    # --- signature with cnf.jwk / cnf.jwk.alg (S3.1)
    if wit_pl and "cnf" in wit_pl:
        jwk = wit_pl["cnf"]["jwk"]; alg = jwk.get("alg")
        if alg not in ACCEPTABLE_ALGS: fails.append(f"cnf.jwk.alg {alg} not acceptable (S3.1)")
        else:
            try:
                base = signature_base(msg, items, params)
                if label not in sv or not verify_raw(alg, jwk, base.encode(), sv[label]):
                    fails.append(f"HTTP signature invalid under cnf.jwk ({alg}) (S3.1)")
            except KeyError as e:
                fails.append(f"cannot build signature base: {e}")
    # --- required parameters (S3)
    for p in ("created", "expires", "nonce", "tag"):
        if p not in pd: fails.append(f"required param {p} missing (S3)")
    if is_req and "wimse-aud" not in pd: fails.append("request lacks wimse-aud (S3, S3.2)")
    if not is_req and "wimse-req-nonce" not in pd: fails.append("response lacks wimse-req-nonce (S3, S3.4/3.5)")
    if "wimse-sign-response" in pd and not isinstance(pd["wimse-sign-response"], bool):
        fails.append("wimse-sign-response not Boolean")
    if policy.reject_keyid_alg:
        for p in ("keyid", "alg"):
            if p in pd: fails.append(f"forbidden param {p} present (S3 'MUST NOT be used'; S3.1 for alg)")
    # --- coverage (S3)
    if policy.enforce_sender_coverage_musts:
        if is_req:
            need = ["@method", "@authority"] if connect else ["@method", "@path", "@query"]
            for n in need:
                if not covered(n): fails.append(f"required component {n} not covered (S3)")
            if connect:
                for n in ("@path", "@query"):
                    if covered(n): fails.append(f"CONNECT request covers {n} (S3 MUST NOT)")
            for h in REQ_HEADERS_IF_PRESENT:
                if msg.hget(h) is not None and not covered(h): fails.append(f"present header {h} not covered (S3)")
        else:
            need = [("@status", False), ("workload-identity-token", False), ("@method", True)]
            need += [("@authority", True)] if connect else [("@path", True), ("@query", True)]
            for n, r in need:
                if not covered(n, r): fails.append(f"required response component {n}{';req' if r else ''} not covered (S3)")
            if connect:
                for n in ("@path", "@query"):
                    if covered(n, True): fails.append(f"CONNECT response covers {n};req (S3 MUST NOT)")
            for h in ("content-type", "content-digest"):
                if msg.hget(h) is not None and not covered(h): fails.append(f"present header {h} not covered (S3)")
    # --- validity window (S3)
    c, e = pd.get("created"), pd.get("expires")
    if isinstance(c, int) and c > now: fails.append("created in the future")
    if isinstance(e, int) and now > e: fails.append(f"outside validity window (expires={e}, now={now}) (S3)")
    if not isinstance(e, int): fails.append("no expires -> validity window undefined")
    # --- audience (S3.2, Simple String Comparison)
    if is_req and "wimse-aud" in pd and pd["wimse-aud"] not in TRUSTED_AUD:
        fails.append(f"wimse-aud {pd['wimse-aud']!r} not in trusted config (S3.2 simple string comparison)")
    # --- response binding (S3.5)
    if not is_req and req_nonce is not None and pd.get("wimse-req-nonce") != req_nonce:
        fails.append(f"wimse-req-nonce {pd.get('wimse-req-nonce')!r} != request nonce (S3.5)")
    # --- content digest (S3 / RFC 9530)
    fails += check_digest(msg)
    return (not fails), fails

def client_check_response(req, resp, now, policy=None):
    """S3.5 client side."""
    rsi = dict(SFParser(req.hget("signature-input")).dictionary())
    rparams = [dict(m[2]) for m in rsi.values() if dict(m[2]).get("tag") == TAG][0]
    signed = resp.hget("signature-input") is not None
    if not signed:
        if rparams.get("wimse-sign-response") is True:
            return False, ["unsigned response but request had wimse-sign-response=?1 (S3.5 client MUST reject)"]
        return True, ["unsigned response accepted (no mandate)"]
    return verify(resp, now, policy, req_nonce=rparams["nonce"])

def server_error_surface(fails):
    # what a conforming server sends for any request-auth failure (S3.6); identical regardless of cause
    return (400, "https://iana.org/assignments/http-problem-types#wimse-signature-invalid")

# --------------------------------------------------------------------------------------------
# vectors (latest values: P-01/P-02/P-06/N-15 from the 2026-11-07 comment)
WIT_A = "eyJhbGciOiJFZDI1NTE5Iiwia2lkIjoiaXNzdWVyLWtleSIsInR5cCI6IndpdCtqd3QifQ.eyJjbmYiOnsiandrIjp7ImFsZyI6IkVkMjU1MTkiLCJjcnYiOiJFZDI1NTE5Iiwia2lkIjoidmVjLWEta2V5Iiwia3R5IjoiT0tQIiwieCI6Ik8zT2ZWbVBKM3BlWWhkRHJNd2VOSWlCT1FVNkpaQ05jWU1LMmtqVjBpM1kifX0sImV4cCI6MTc5NTAwMzYwMCwiaWF0IjoxNzk0OTk5OTQwLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tL2lzc3VlciIsImp0aSI6IndpdC1hLTE3OTUwMDAwMDAiLCJzdWIiOiJ3aW1zZTovL2V4YW1wbGUuY29tL3N2Y0EifQ.JCh9sN__1Al9xVB-K7CFafw1tDV8PCeZvyKdFyMmb9vvN4mK2ZGNbC6VLFpNzpVsgGBV0FwmzerDAFuikSJBCw"
WIT_B = "eyJhbGciOiJFZDI1NTE5Iiwia2lkIjoiaXNzdWVyLWtleSIsInR5cCI6IndpdCtqd3QifQ.eyJjbmYiOnsiandrIjp7ImFsZyI6IkVkMjU1MTkiLCJjcnYiOiJFZDI1NTE5Iiwia2lkIjoidmVjLWIta2V5Iiwia3R5IjoiT0tQIiwieCI6IjRqVkF6Z0VQTzVuLTZqdWpTaXlRTUU1dC10SXpaQXBiaFI1Y1RQb2VkSUkifX0sImV4cCI6MTc5NTAwMzYwMCwiaWF0IjoxNzk0OTk5OTQwLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tL2lzc3VlciIsImp0aSI6IndpdC1iLTE3OTUwMDAwMDAiLCJzdWIiOiJ3aW1zZTovL2V4YW1wbGUuY29tL3N2Y0IifQ.iBAAT-2xF6Polfa49cDu4THgh3zhCdbAitBM5JIgxuuCEdbjMKglKVskt7E78jdE42i3FMMP9-Lw0PLRXwXaBQ"
WIT_C = "eyJhbGciOiJFZDI1NTE5Iiwia2lkIjoiaXNzdWVyLWtleSIsInR5cCI6IndpdCtqd3QifQ.eyJjbmYiOnsiandrIjp7ImFsZyI6IkVTMjU2IiwiY3J2IjoiUC0yNTYiLCJraWQiOiJ2ZWMtYy1rZXkiLCJrdHkiOiJFQyIsIngiOiJqWmpmVUJRZ0QxbDlSX2xtNG56bzFyUDgycEdWREJ4SEQ2WW1Pb194b0NvIiwieSI6IkNCR3Y5YjhoQi1sMG1vdjlybHUyMjNnLXZORV9TcXVDQzJJaFBpMkl3ZUUifX0sImV4cCI6MTc5NTAwMzYwMCwiaWF0IjoxNzk0OTk5OTQwLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tL2lzc3VlciIsImp0aSI6IndpdC1jLTE3OTUwMDAwMDAiLCJzdWIiOiJ3aW1zZTovL2V4YW1wbGUuY29tL3N2Y0MifQ.8-bmHNavOVSxyr2hAtnKfrC-kdm5L4XMP4n1cGGMLh5DjSPmdjTWkpKtTO9tPZfKMIfLVC7xGaDvoJXUdizGCg"

SIG = {
    "P-01": "qrIGE6wS80/UvhJx96iDiz90OIYmUX8CFO4vOeK/40D7pnukeikqvsYGDs6aqXx099ILxgZliEepCw1P5M7YDg==",
    "P-02": "XugjjXCtpc0lkt5QSnjVF/OcQwqhQAqAzuykBUw36FsGV6BmXcMKfY0YZTMTnvpsjIZkmOeTN+PvQEzAb/veDQ==",
    "P-03": "n7QUfcBz5ruH3anRYFpW7drn1CInZfV4TZPxlqBIlHg1g78FnRhk7CQudkHN8kNGAHfsBTgIvfHGJMZ8f2QTbQ==",
    "P-04": "H00PodGDV4favyn4jdnlaimqFLZy8v1wikMXq5JAFSrQvTnkJ4MGtNZw5XM4DiXYs1ubaCnQoqLuyagNlV0IDw==",
    "P-05": "62NICDRikwhl4IlI2ls8cGIACVyuFNtmSZdYOZKiO88AqsKZLQuybOkQx5SQYkREcB0OiU4xT+qn9/hoAj1LAg==",
    "P-06-sig1": "C9vDZlqwPqD3dPtkwhQDz0cmpsy0Z2tSE/ewIHjMCdgmdNN7nqrZTLLZqGobMOjswZF43HMaJXGGjFVuRYB5BQ==",
    "P-06-sig2": "Dyr5ErLhw5LmeYIztg6QZmfARn96ucIGuMXUgsyGj9MMc4Y9cQmQ6345/c8/n584kmlk1TfL7xmNVDQKkG7EAw==",
    "N-15": "28GmtKZAQJ1w6QtPGGrrrXMhdSgWXCmMbTVIuFNUh+PvOWS1oySwSUAPGhhvoad18zrTZXYh/Dh0ixcHcfB77g==",
}
STALE = {  # values in the issue body (pre-2026-11-07)
    "P-01": "9NW0p6RymixUlZEKptq1OiX/XS0qNcaNNUUdDfD3APJ6t96WoVtI+cV/xN5kW6DOkSEIInP1MR+/RVYG9ZEsBA==",
    "P-02": "OjMFe4m65+aMby0HKr9d3oYPRKKqHMV8rS7bnfy609XAUJhGIUlyUl1eNRvkIFNHaakxPlSnf1oj2u8NISA6BQ==",
    "P-06-sig2": "WMzq6kTy1tgM9BlBBpIKXT5B3cVYWJbl2QK+27KfcBAqkN/5GuHIMt/NzjqOTnN8MVrrS/2SmirYhWdJmhP/Cg==",
    "N-15": "6M4HL8Uqn5vOPzPw0F/6lgMdqQXY/qk/HxbJLYxDK3ykuZboIL/OeDbMZ81Pvc8k/O0iuhNAaoF8UWK+SDmySQ==",
}

SI = {
    "P-01": 'sig1=("@method" "@path" "@query" "workload-identity-token");created=1795000000;expires=1795000300;nonce="7f3a9c1e5b284d06a1f4e8c2b6d50937";tag="wimse-workload-to-workload";wimse-aud="https://svcb.example.com/gimme-ice-cream";wimse-sign-response',
    "P-02": 'sig1=("@status" "workload-identity-token" "content-type" "content-digest" "@method";req "@path";req "@query";req);created=1795000002;expires=1795000302;nonce="2b8e4f0a9d1c3756e0a2b4c6d8f0a1b3";tag="wimse-workload-to-workload";wimse-req-nonce="7f3a9c1e5b284d06a1f4e8c2b6d50937"',
    "P-03": 'sig1=("@method" "@path" "@query" "workload-identity-token" "content-type" "content-digest");created=1795000000;expires=1795000300;nonce="c51d7a2e8f093b46a5c1d2e3f4a5b6c7";tag="wimse-workload-to-workload";wimse-aud="https://svcb.example.com/inventory/cones"',
    "P-04": 'sig1=("@method" "@authority" "workload-identity-token");created=1795000000;expires=1795000300;nonce="9a0b1c2d3e4f5061728394a5b6c7d8e9";tag="wimse-workload-to-workload";wimse-aud="https://svcb.example.com"',
    "P-05": 'sig1=("@method" "@path" "@query" "workload-identity-token");created=1795000000;expires=1795000300;nonce="13579bdf2468ace013579bdf2468ace0";tag="wimse-workload-to-workload";wimse-aud="https://svcb.example.com/status"',
    "P-06": 'sig1=("@method" "@path");created=1795000000;keyid="other-key";tag="example-other", sig2=("@method" "@path" "@query" "workload-identity-token");created=1795000000;expires=1795000300;nonce="f0e1d2c3b4a5968778695a4b3c2d1e0f";tag="wimse-workload-to-workload";wimse-aud="https://svcb.example.com/gimme-ice-cream"',
    "N-15": 'sig1=("@method" "@path" "@query" "workload-identity-token");created=1795000000;expires=1795000300;nonce="abcdef0123456789abcdef0123456789";tag="wimse-workload-to-workload";wimse-aud="https://svcb.example.com/gimme-ice-cream"',
}

def req(method, target, host, wit, si, sig, extra=(), body=b""):
    h = [("Host", host), *extra, ("Workload-Identity-Token", wit), ("Signature-Input", si), ("Signature", sig)]
    return Msg("request", h, body, method=method, target=target)

def P01(): return req("GET", "/gimme-ice-cream?flavor=vanilla", "svcb.example.com", WIT_A, SI["P-01"], f"sig1=:{SIG['P-01']}:")
def P02(request=None):
    body = b"No ice cream today.\n"
    h = [("Content-Type", "text/plain"), ("Content-Digest", "sha-256=:uJC3qmCc7n6/6w4N2I0vAfj1cd/hTOAhxLEYXmPbNno=:"),
         ("Workload-Identity-Token", WIT_B), ("Signature-Input", SI["P-02"]), ("Signature", f"sig1=:{SIG['P-02']}:")]
    return Msg("response", h, body, status=404, request=request or P01())
P03_BODY = b'{"flavor":"vanilla","amount":1}'
def P03(): return req("POST", "/inventory/cones", "svcb.example.com", WIT_C, SI["P-03"], f"sig1=:{SIG['P-03']}:",
                      extra=[("Content-Type", "application/json"), ("Content-Digest", "sha-256=:TzKXT0tUEfiTFkjRzwE8nCFnQljMuX5xwJaJgJCp+1g=:")], body=P03_BODY)
def P04(): return req("CONNECT", "svcb.example.com:443", "svcb.example.com:443", WIT_A, SI["P-04"], f"sig1=:{SIG['P-04']}:")
def P05(): return req("GET", "/status", "svcb.example.com", WIT_A, SI["P-05"], f"sig1=:{SIG['P-05']}:")
def P06(): return req("GET", "/gimme-ice-cream?flavor=vanilla", "svcb.example.com", WIT_A, SI["P-06"],
                      f"sig1=:{SIG['P-06-sig1']}:, sig2=:{SIG['P-06-sig2']}:")

def first_sig(msg, label=None):
    si = SFParser(msg.hget("signature-input")).dictionary()
    for k, m in si:
        if label is None or k == label: return k, m[1], m[2]

def params_of(si_line, label="sig1"):
    for k, m in SFParser(si_line).dictionary():
        if k == label: return m[1], m[2]

def resign(msg, keyname, items=None, params=None, label="sig1", transform=None):
    """Re-sign msg's (single) WIMSE signature after applying a variation to its items/params."""
    _, it0, pa0 = first_sig(msg, label)
    items = items if items is not None else it0
    params = params if params is not None else pa0
    m = msg.copy(); m.hset("Signature-Input", None); m.hset("Signature", None)
    if transform: transform(m)
    return sign_msg(m, label, items, params, keyname)

def setp(params, k, v):
    out = [(a, b) for a, b in params if a != k]
    if v is not None:
        # keep tag / wimse-* ordering roughly: append
        out.append((k, v))
    return out

def insert_after(params, after, k, v):
    out = []
    for a, b in params:
        out.append((a, b))
        if a == after: out.append((k, v))
    return out

# --------------------------------------------------------------------------------------------
LOG = []
def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print(s)

def run():
    results = []
    def record(vid, expected, accept, fails, note=""):
        got = "accept" if accept else "reject"
        results.append((vid, expected, got, expected == got, note))
        log(f"[{vid}] expected={expected} got={got} {'MATCH' if expected==got else 'MISMATCH'}")
        for f in fails: log(f"    - {f}")
        if note: log(f"    note: {note}")

    log("=== 0. key material self-consistency")
    for n, j in KEYS.items():
        pk = priv_from_jwk(j).public_key()
        if j["kty"] == "OKP":
            from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
            ok = b64u_enc(pk.public_bytes(Encoding.Raw, PublicFormat.Raw)) == j["x"]
        else:
            nums = pk.public_numbers()
            ok = b64u_enc(nums.x.to_bytes(32, "big")) == j["x"] and b64u_enc(nums.y.to_bytes(32, "big")) == j["y"]
        log(f"  {n}: d -> x{'/y' if j['kty']=='EC' else ''} matches published public key: {ok}")
    # derivation formula (issue: seed = SHA-256("s01-validation-vectors:<name>"))
    for n, lbl in (("issuer", "issuer"), ("svcA", "svcA"), ("svcB", "svcB"), ("other", "other")):
        seed = hashlib.sha256(f"s01-validation-vectors:{lbl}".encode()).digest()
        log(f"  derivation {n}: SHA-256('s01-validation-vectors:{lbl}') == d: {b64u_enc(seed) == KEYS[n]['d']}")
    nP = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    dC = int.from_bytes(hashlib.sha256(b"s01-validation-vectors:svcC").digest(), "big") % (nP - 1) + 1
    log(f"  derivation svcC: SHA-256('s01-validation-vectors:svcC') mod (n-1)+1 == d: {b64u_enc(dC.to_bytes(32,'big')) == KEYS['svcC']['d']}")
    for nm, w in (("WIT-A", WIT_A), ("WIT-B", WIT_B), ("WIT-C", WIT_C)):
        pl, errs = validate_wit(w, NOW)
        log(f"  {nm}: errs={errs} sub={pl['sub']} cnf.kid={pl['cnf']['jwk']['kid']} exp-T0={pl['exp']-T0} iat-T0={pl['iat']-T0}")

    log("\n=== 1. reproduce published signatures byte-for-byte with my base construction + the published private keys")
    for vid, mk, key, label in (("P-01", P01, "svcA", "sig1"), ("P-03", P03, "svcC", "sig1"), ("P-04", P04, "svcA", "sig1"),
                                ("P-05", P05, "svcA", "sig1"), ("P-06-sig2", P06, "svcA", "sig2"), ("P-06-sig1", P06, "other", "sig1")):
        m = mk(); _, it, pa = first_sig(m, label)
        base = signature_base(m, it, pa)
        mine = base64.b64encode(sign_raw(KEYS[key], base.encode())).decode()
        log(f"  {vid}: regenerated == published: {mine == SIG[vid]}")
    m = P02(); _, it, pa = first_sig(m)
    mine = base64.b64encode(sign_raw(KEYS["svcB"], signature_base(m, it, pa).encode())).decode()
    log(f"  P-02: regenerated == published: {mine == SIG['P-02']}")
    m = req("GET", "/gimme-ice-cream?flavor=vanilla", "svcb.example.com", WIT_A, SI["N-15"], "sig1=:AA==:")
    _, it, pa = first_sig(m)
    base15 = signature_base(m, it, pa)
    mine = base64.b64encode(sign_raw(KEYS["svcC"], base15.encode())).decode()
    log(f"  N-15 (ES256, RFC 6979 via cryptography deterministic_signing): regenerated == published: {mine == SIG['N-15']}")
    log("  P-01 signature base as I build it:")
    m = P01(); _, it, pa = first_sig(m)
    for ln in signature_base(m, it, pa).split("\n"): log("    | " + (ln[:90] + "..." if len(ln) > 90 else ln))

    log("\n=== 2. stale (issue-body) values: check the 2026-11-07 comment's claim")
    def base_without_qmark(b): return b.replace('"@query": ?flavor=vanilla', '"@query": flavor=vanilla').replace('"@query";req: ?flavor=vanilla', '"@query";req: flavor=vanilla')
    for vid, mk, key, label, alg in (("P-01", P01, "svcA", "sig1", "Ed25519"), ("P-06-sig2", P06, "svcA", "sig2", "Ed25519")):
        m = mk(); _, it, pa = first_sig(m, label); b = signature_base(m, it, pa)
        old = base64.b64decode(STALE[vid]); new = base64.b64decode(SIG[vid])
        log(f"  {vid}: stale/corrected-base={verify_raw(alg, pubjwk(key), b.encode(), old)} stale/no-?-base={verify_raw(alg, pubjwk(key), base_without_qmark(b).encode(), old)} "
            f"new/corrected-base={verify_raw(alg, pubjwk(key), b.encode(), new)} new/no-?-base={verify_raw(alg, pubjwk(key), base_without_qmark(b).encode(), new)}")
    m = P02(); _, it, pa = first_sig(m); b = signature_base(m, it, pa)
    old = base64.b64decode(STALE["P-02"]); new = base64.b64decode(SIG["P-02"])
    log(f"  P-02: stale/corrected-base={verify_raw('Ed25519', pubjwk('svcB'), b.encode(), old)} stale/no-?-base={verify_raw('Ed25519', pubjwk('svcB'), base_without_qmark(b).encode(), old)} new/corrected-base={verify_raw('Ed25519', pubjwk('svcB'), b.encode(), new)}")
    old = base64.b64decode(STALE["N-15"]); new = base64.b64decode(SIG["N-15"])
    log(f"  N-15 under svcC key: stale/corrected-base={verify_raw('ES256', pubjwk('svcC'), base15.encode(), old)} stale/no-?-base={verify_raw('ES256', pubjwk('svcC'), base_without_qmark(base15).encode(), old)} new/corrected-base={verify_raw('ES256', pubjwk('svcC'), base15.encode(), new)}")

    log("\n=== 3. positive vectors (verification time T0+60)")
    for vid, mk in (("P-01", P01), ("P-03", P03), ("P-04", P04), ("P-05", P05), ("P-06", P06)):
        ok, f = verify(mk(), NOW); record(vid, "accept", ok, f)
    ok, f = client_check_response(P01(), P02(), NOW); record("P-02", "accept", ok, f, "client-side check, wimse-req-nonce bound to P-01 nonce")
    ok, f = verify(P06(), NOW, Policy(reject_keyid_alg=False)); log(f"  (P-06 decoy sig1 carries keyid; irrelevant because it is not the tagged signature; accept={ok})")
    m = P06(); _, it, pa = first_sig(m, "sig1")
    log(f"  (P-06 decoy sig1 verifies under other-key: {verify_raw('Ed25519', pubjwk('other'), signature_base(m, it, pa).encode(), base64.b64decode(SIG['P-06-sig1']))})")

    log("\n=== 4. negative vectors")
    E = "reject"
    # N-01: drop @query (re-signed so only the variation differs; also run un-re-signed)
    _, it, pa = first_sig(P01())
    m = resign(P01(), "svcA", items=[x for x in it if x[0] != "@query"])
    ok, f = verify(m, NOW); record("N-01", E, ok, f, "re-signed variant; signature itself is valid")
    ok2, f2 = verify(m, NOW, Policy(enforce_sender_coverage_musts=False)); log(f"    with sender-coverage MUSTs not enforced on receive: accept={ok2} {f2}")
    # N-02: CONNECT + @path
    _, it, pa = first_sig(P04())
    m = resign(P04(), "svcA", items=it[:2] + [("@path", [])] + it[2:])
    log("    N-02 base @path value: " + [l for l in signature_base(m, *first_sig(m)[1:]).split("\n") if l.startswith('"@path"')][0])
    ok, f = verify(m, NOW); record("N-02", E, ok, f, "re-signed variant")
    ok2, f2 = verify(m, NOW, Policy(enforce_sender_coverage_musts=False)); log(f"    with sender-coverage MUSTs not enforced on receive: accept={ok2} {f2}")
    # N-03: no Content-Digest
    _, it, pa = first_sig(P03())
    m = resign(P03(), "svcC", items=[x for x in it if x[0] != "content-digest"], transform=lambda mm: mm.hset("Content-Digest", None))
    ok, f = verify(m, NOW); record("N-03", E, ok, f, "re-signed variant")
    # N-04: body swapped, header unchanged (NOT re-signed - the issue does not re-sign)
    m = P03(); m.body = b'{"flavor":"chocolate","amount":1}'
    ok, f = verify(m, NOW); record("N-04", E, ok, f, "issue says this 'also makes the signature fail' - see whether the signature failure appears above")
    # N-05: no expires
    _, it, pa = first_sig(P01())
    m = resign(P01(), "svcA", params=[p for p in pa if p[0] != "expires"])
    ok, f = verify(m, NOW); record("N-05", E, ok, f, "re-signed variant")
    m_nr = P01(); m_nr.hset("Signature-Input", SI["P-01"].replace(";expires=1795000300", ""))
    ok2, f2 = verify(m_nr, NOW); log(f"    not re-signed variant: accept={ok2} {f2}")
    # N-06: keyid
    m = resign(P01(), "svcA", params=insert_after(pa, "expires", "keyid", "vec-a-key"))
    ok, f = verify(m, NOW); record("N-06", E, ok, f, "re-signed; crypto-valid")
    ok2, f2 = verify(m, NOW, Policy(reject_keyid_alg=False)); log(f"    verifier that does not reject keyid on receive: accept={ok2} {f2}")
    # N-07: alg
    m = resign(P01(), "svcA", params=insert_after(pa, "expires", "alg", "ed25519"))
    ok, f = verify(m, NOW); record("N-07", E, ok, f, "re-signed; crypto-valid")
    ok2, f2 = verify(m, NOW, Policy(reject_keyid_alg=False)); log(f"    verifier that does not reject alg on receive: accept={ok2} {f2}")
    # N-08: two WIMSE tags
    m6 = P06(); _, it1, pa1 = first_sig(m6, "sig1"); _, it2, pa2 = first_sig(m6, "sig2")
    m = m6.copy(); m.hset("Signature-Input", None); m.hset("Signature", None)
    pa1b = [(k, (TAG if k == "tag" else v)) for k, v in pa1]
    sign_msg(m, "sig1", it1, pa1b, "other")
    si1, sv1 = m.hget("Signature-Input"), m.hget("Signature")
    sign_msg(m, "sig2", it2, pa2, "svcA", existing=(si1, sv1))
    ok, f = verify(m, NOW); record("N-08", E, ok, f)
    # N-09: verify at T0+3600
    ok, f = verify(P01(), T0 + 3600); record("N-09", E, ok, f, "WIT-A exp == T0+3600, so the WIT exp check also trips at this instant")
    ok2, f2 = verify(P01(), T0 + 301); log(f"    control at T0+301 (sig window only): accept={ok2} {f2}")
    # N-10: trailing slash aud
    m = resign(P01(), "svcA", params=[(k, ("https://svcb.example.com/gimme-ice-cream/" if k == "wimse-aud" else v)) for k, v in pa])
    ok, f = verify(m, NOW); record("N-10", E, ok, f, "re-signed")
    # N-11: no wimse-aud
    m = resign(P01(), "svcA", params=[p for p in pa if p[0] != "wimse-aud"])
    ok, f = verify(m, NOW); record("N-11", E, ok, f, "re-signed")
    # N-12: response without wimse-req-nonce
    _, itr, par = first_sig(P02())
    m = resign(P02(), "svcB", params=[p for p in par if p[0] != "wimse-req-nonce"])
    ok, f = client_check_response(P01(), m, NOW); record("N-12", E, ok, f, "re-signed response")
    # N-13: wrong req nonce
    m = resign(P02(), "svcB", params=[(k, ("0" * 32 if k == "wimse-req-nonce" else v)) for k, v in par])
    ok, f = client_check_response(P01(), m, NOW); record("N-13", E, ok, f, "re-signed response")
    # N-14: unsigned response
    m = P02(); m.hset("Signature-Input", None); m.hset("Signature", None)
    ok, f = client_check_response(P01(), m, NOW); record("N-14", E, ok, f)
    # N-15
    m = req("GET", "/gimme-ice-cream?flavor=vanilla", "svcb.example.com", WIT_A, SI["N-15"], f"sig1=:{SIG['N-15']}:")
    ok, f = verify(m, NOW)
    record("N-15", E, ok, f, f"published sig valid under svcC ES256 key: {verify_raw('ES256', pubjwk('svcC'), base15.encode(), base64.b64decode(SIG['N-15']))}")
    # N-16: sender nonce entropy (harness level)
    import secrets
    weak = [secrets.token_hex(4) for _ in range(1000)]
    bits = lambda n: len(n) * 4 if re.fullmatch(r"[0-9a-f]+", n) else None
    log(f"[N-16] harness: 1000 nonces from a 32-bit (8-hex) generator -> max representable entropy {max(bits(n) for n in weak)} bits < 64 -> sender NOT conformant")
    log(f"    lint applied to the vector nonces: " + ", ".join(f"{v}={bits(n)}b" for v, n in (("P-01", "7f3a9c1e5b284d06a1f4e8c2b6d50937"), ("N-15", "abcdef0123456789abcdef0123456789"))))
    log(f"    lint applied to draft -08 Figure 2/4/6/7 nonces abcd1111..abcd4444 -> {bits('abcd1111')} bits (O-2)")
    results.append(("N-16", "sender not conformant", "sender not conformant (harness)", True, "behavioural; not a single-message vector"))
    # N-17: error surface of THIS verifier for a WIT failure vs a signature failure
    wit_exp = make_jwt({**json.loads(b64u_dec(WIT_A.split(".")[1])), "exp": T0 + 30})
    m_wit = resign(req("GET", "/gimme-ice-cream?flavor=vanilla", "svcb.example.com", wit_exp, SI["P-01"], "sig1=:AA==:"), "svcA")
    m_sig = P01(); m_sig.hset("Signature", "sig1=:" + base64.b64encode(b"\0" * 64).decode() + ":")
    a1, f1 = verify(m_wit, NOW); a2, f2 = verify(m_sig, NOW)
    log(f"[N-17] probe: WIT-expired request -> accept={a1} causes={f1}; bad-signature request -> accept={a2} causes={f2}")
    log(f"    error surface emitted: {server_error_surface(f1)} vs {server_error_surface(f2)} -> identical={server_error_surface(f1)==server_error_surface(f2)}")
    log("    (server conformance can only be judged against a real server; a server that returns these causes in the body or 401 is non-conformant by S3.6)")
    results.append(("N-17", "server not conformant", "n/a (server behaviour)", None, "probe messages built; my verifier's surface is uniform 400"))
    # N-18
    def server_conformance(req_m, status, signed, supports_signing):
        mandate = dict(first_sig(req_m)[2]).get("wimse-sign-response") is True
        if not mandate or signed: return True
        if 200 <= status < 300: return False
        return status == (501 if not supports_signing else 400)
    log(f"[N-18] checker: 200 unsigned after wimse-sign-response -> conformant={server_conformance(P01(), 200, False, False)}; "
        f"501 when unsupported -> {server_conformance(P01(), 501, False, False)}; 400 when supported-but-unavailable -> {server_conformance(P01(), 400, False, True)}; "
        f"400 when unsupported -> {server_conformance(P01(), 400, False, False)}")
    results.append(("N-18", "server not conformant", "server not conformant (checker)", True, "behavioural"))
    # N-19: Accept-Signature weaker coverage
    acc = 'sig1=("@status");tag="wimse-workload-to-workload"'
    req_set = {("@status", ()), ("workload-identity-token", ()), ("@method", (("req", True),)), ("@path", (("req", True),)), ("@query", (("req", True),))}
    got = {(v, tuple(sorted(dict(p).items()))) for v, p in SFParser(acc).dictionary()[0][1][1]}
    log(f"[N-19] Accept-Signature {acc} covers required response set: {req_set <= got} -> sender {'conformant' if req_set <= got else 'NOT conformant'}")
    results.append(("N-19", "sender not conformant", "sender not conformant (checker)", True, "behavioural"))
    # N-20: expired WIT, crypto-valid message signature
    ok, f = verify(m_wit, NOW)
    log(f"[N-20] probe: expired WIT + valid HTTP sig -> accept={ok} causes={f}")
    log("    (ordering 'WIT before signature, nothing processed before full validation' is an implementation property; this verifier validates the WIT first)")
    results.append(("N-20", "verifier not conformant", "probe rejected (my verifier)", None, "behavioural; ordering cannot be observed from one message"))
    # N-21: CONNECT response covering @path;req
    p04 = P04()
    def connect_resp(items):
        body = b"No ice cream today.\n"
        r = Msg("response", [("Content-Type", "text/plain"), ("Content-Digest", "sha-256=:uJC3qmCc7n6/6w4N2I0vAfj1cd/hTOAhxLEYXmPbNno=:"), ("Workload-Identity-Token", WIT_B)],
                body, status=404, request=p04)
        prm = [("created", T0 + 2), ("expires", T0 + 302), ("nonce", "2b8e4f0a9d1c3756e0a2b4c6d8f0a1b3"), ("tag", TAG), ("wimse-req-nonce", "9a0b1c2d3e4f5061728394a5b6c7d8e9")]
        return sign_msg(r, "sig1", items, prm, "svcB")
    good = connect_resp(C("@status", "workload-identity-token", "content-type", "content-digest", "@method;req", "@authority;req"))
    ok, f = client_check_response(p04, good, NOW); log(f"    N-21 control (CONNECT response with @method;req @authority;req): accept={ok} {f}")
    bad = connect_resp(C("@status", "workload-identity-token", "content-type", "content-digest", "@method;req", "@authority;req", "@path;req"))
    ok, f = client_check_response(p04, bad, NOW); record("N-21", E, ok, f, "constructed (issue gives no literal values); re-signed")
    ok2, f2 = client_check_response(p04, bad, NOW, Policy(enforce_sender_coverage_musts=False)); log(f"    with sender-coverage MUSTs not enforced on receive: accept={ok2} {f2}")
    # N-22: label selection
    okt, ft = verify(P06(), NOW, Policy(select="tag")); okl, fl = verify(P06(), NOW, Policy(select="first-label"))
    log(f"[N-22] P-06 by tag: accept={okt} {ft}; by first label (strawman): accept={okl} {fl}")
    results.append(("N-22", "verifier not conformant", "label-picker diverges from tag-picker" if okt != okl else "no divergence", okt != okl, "behavioural"))

    log("\n=== 5. sanity: draft -08 Section 3.7 examples (HTTP signature only; draft issuer key not published)")
    inc = sys.argv[1] if len(sys.argv) > 1 else None
    if inc and os.path.isdir(inc):
        def load(fn):
            raw = open(os.path.join(inc, fn), "rb").read().decode()
            head, _, body = raw.partition("\n\n")
            return parse_http(head, body.encode())
        def cnf(m): return json.loads(b64u_dec(m.hget("workload-identity-token").split(".")[1]))["cnf"]["jwk"]
        r1 = load("sigs-request.txt"); s1 = load("sigs-response.txt"); s1.request = r1
        r2 = load("sigs-request-b-c.txt"); s2 = load("sigs-response-c.txt"); s2.request = r2
        for nm, m in (("Fig2 request", r1), ("Fig4 response", s1), ("Fig6 request b-c", r2), ("Fig7 response c", s2)):
            lab, it, pa = first_sig(m); j = cnf(m)
            sv = dict((k, mm[1]) for k, mm in SFParser(m.hget("signature")).dictionary())
            okv = verify_raw(j["alg"], j, signature_base(m, it, pa).encode(), sv[lab])
            log(f"  {nm}: HTTP signature verifies under cnf.jwk ({j['alg']}): {okv}; digest errs={check_digest(m)}")
    else:
        log("  (skipped: pass the includes/ dir as argv[1])")

    log("\n=== summary")
    log(f"{'ID':6} {'expected':26} {'got':40} match")
    for vid, e, g, mt, note in results:
        log(f"{vid:6} {e:26} {g:40} {'yes' if mt else ('n/a' if mt is None else 'NO')}")
    return results

if __name__ == "__main__":
    run()
