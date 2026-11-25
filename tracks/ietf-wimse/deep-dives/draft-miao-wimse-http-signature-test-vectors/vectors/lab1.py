"""Lab 1 for draft-miao-wimse-http-signature-test-vectors-00.

Re-derives the five test keys from their published seeds (Section 3),
checks the WIT-A issuer signature, and re-signs the P-01 signature base
(Section 4.1) once with the WIT placeholder and once with the full WIT-A
text. Run: python3 -I vectors/lab1.py > vectors/lab1.log
"""

import base64, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def b64u(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


ed = {
    "issuer": ("QH_Zu0pnwyO8xdFQm9upOUFAbpb4nhMrGc29L3uJXDA", "4nRAPQQyr8cUgAtCESLc4ZIGIxZT9-guqxcc3wV-2NI"),
    "svcA": ("O3OfVmPJ3peYhdDrMweNIiBOQU6JZCNcYMK2kjV0i3Y", "F8BhX5poMswcVwTgEMGETOhdN72PaxIiwuGYWrzSUvk"),
    "svcB": ("4jVAzgEPO5n-6jujSiyQME5t-tIzZApbhR5cTPoedII", "4MaIKp1h5mkTS7ZSawz6QYN6FYA_rOYBPDfGEZCpPDg"),
    "other": ("Lo6grJBjN252d2huS1-ckJIql2FZR2vrTOF2qKRBTm4", "KL4_B1CdV7qwZkVYvyK0I5SrsEzv6yb1p1PNAfbC7LY"),
}
keys = {}
for name, (x, d) in ed.items():
    seed = hashlib.sha256(f"s01-validation-vectors:{name}".encode()).digest()
    k = Ed25519PrivateKey.from_private_bytes(seed)
    pub = k.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    keys[name] = k
    print(name, "d matches:", b64u(seed) == d, "x matches:", b64u(pub) == x)

n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
s = int.from_bytes(hashlib.sha256(b"s01-validation-vectors:svcC").digest(), "big") % (n - 1) + 1
c = ec.derive_private_key(s, ec.SECP256R1())
nums = c.public_key().public_numbers()
print("svcC d matches:", b64u(s.to_bytes(32, "big")) == "X94ti7AkOiC4JcxdbSmLkwWEzyEU4wMqBX_9LHfXQaU",
      "x matches:", b64u(nums.x.to_bytes(32, "big")) == "jZjfUBQgD1l9R_lm4nzo1rP82pGVDBxHD6YmOo_xoCo",
      "y matches:", b64u(nums.y.to_bytes(32, "big")) == "CBGv9b8hB-l0mov9rlu223g-vNE_SquCC2IhPi2IweE")

wita = "eyJhbGciOiJFZDI1NTE5Iiwia2lkIjoiaXNzdWVyLWtleSIsInR5cCI6IndpdCtqd3QifQ.eyJjbmYiOnsiandrIjp7ImFsZyI6IkVkMjU1MTkiLCJjcnYiOiJFZDI1NTE5Iiwia2lkIjoidmVjLWEta2V5Iiwia3R5IjoiT0tQIiwieCI6Ik8zT2ZWbVBKM3BlWWhkRHJNd2VOSWlCT1FVNkpaQ05jWU1LMmtqVjBpM1kifX0sImV4cCI6MTc5NTAwMzYwMCwiaWF0IjoxNzk0OTk5OTQwLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tL2lzc3VlciIsImp0aSI6IndpdC1hLTE3OTUwMDAwMDAiLCJzdWIiOiJ3aW1zZTovL2V4YW1wbGUuY29tL3N2Y0EifQ.JCh9sN__1Al9xVB-K7CFafw1tDV8PCeZvyKdFyMmb9vvN4mK2ZGNbC6VLFpNzpVsgGBV0FwmzerDAFuikSJBCw"
h, p, sg = wita.split(".")
try:
    keys["issuer"].public_key().verify(base64.urlsafe_b64decode(sg + "=="), f"{h}.{p}".encode())
    print("WIT-A issuer signature verifies")
except Exception:
    print("WIT-A issuer signature FAILS")
print("WIT-A payload:", base64.urlsafe_b64decode(p + "==").decode())

params = '("@method" "@path" "@query" "workload-identity-token");created=1795000000;expires=1795000300;nonce="7f3a9c1e5b284d06a1f4e8c2b6d50937";tag="wimse-workload-to-workload";wimse-aud="https://svcb.example.com/gimme-ice-cream";wimse-sign-response'
want = "qrIGE6wS80/UvhJx96iDiz90OIYmUX8CFO4vOeK/40D7pnukeikqvsYGDs6aqXx099ILxgZliEepCw1P5M7YDg=="
for label, w in [("placeholder [WIT-A，§2 全文]", "[WIT-A，§2 全文]"), ("full WIT-A text", wita)]:
    base = f'"@method": GET\n"@path": /gimme-ice-cream\n"@query": ?flavor=vanilla\n"workload-identity-token": {w}\n"@signature-params": {params}'
    got = base64.b64encode(keys["svcA"].sign(base.encode())).decode()
    print("P-01 re-sign over", label, "byte-identical:", got == want)
