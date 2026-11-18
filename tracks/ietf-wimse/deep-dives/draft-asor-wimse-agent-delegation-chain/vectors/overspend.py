#!/usr/bin/env python3
"""Lab 2: the two-gateway overspend of Section 9.4 of
draft-asor-wimse-agent-delegation-chain-03, then the two deployment shapes the
section names (a shared atomic ledger, and a single-writer allocator with local
enforcement) and the hazards each one has to handle.

Chains are minted with Ed25519 and checked with verify_vectors.py (steps 1-5 and
the audience part of step 8). Gateways, ledger and allocator are small in-process
models written for this lab; threads stand in for two gateways racing.

Usage: python3 -I overspend.py
"""

import copy
import hashlib
import importlib.util
import os
import platform
import sys
import threading

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("vv", os.path.join(HERE, "verify_vectors.py"))
vv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vv)

ROOT = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"asor-lab2:root").digest())
KEYS = {"root-1": ("Ed25519", ROOT)}
HEADER = {"alg": "Ed25519", "kid": "root-1", "typ": "at+jwt"}
BUDGET = 100
NOW = 1500


def mint_chain(child_cons, root_cons, client_id, gw):
    common = {"iss": "https://as.example.com", "sub": "org:acme-finance", "iat": 1000}
    p0 = dict(common, aud=["https://gw-a.example.com", "https://gw-b.example.com"], client_id="planner",
              jti="lab2:root", exp=4600, del_depth=0, del_max_depth=3, cnf={"jkt": "planner-jkt"},
              authorization_details=[{"type": "agent_delegation", "scopes": ["pay.send"], "constraints": root_cons}])
    t0 = vv.mint(HEADER, p0, "Ed25519", ROOT)
    p1 = dict(common, aud=gw, client_id=client_id, jti="lab2:" + client_id, exp=2800, del_depth=1,
              cnf={"jkt": client_id + "-jkt"}, par_hash=vv.par_hash(t0),
              authorization_details=[{"type": "agent_delegation", "scopes": ["pay.send"], "constraints": child_cons}])
    return [t0, vv.mint(HEADER, p1, "Ed25519", ROOT)]


def verify(chain, gw):
    return vv.run(chain, keys=KEYS, accepted_algs=["Ed25519"], now=NOW, audience=gw)


def leaf(chain):
    import json
    return json.loads(vv.b64d(chain[-1].split(".")[1]))


def per_action_max(chain, key):
    for c in leaf(chain)["authorization_details"][0]["constraints"]:
        if c["key"] == key and "max" in c:
            return c["max"]
    return None


def step8(chain, amount, subtree_total, skip_cumulative=False):
    """Action part of step 8 for max_spend only: per-action max against the request,
    max_subtree against a total held outside the request (None = not held)."""
    for c in leaf(chain)["authorization_details"][0]["constraints"]:
        if "max" in c and amount > c["max"]:
            return False
        if "max_subtree" in c and not skip_cumulative:
            if subtree_total is None or subtree_total + amount > c["max_subtree"]:
                return False
    return True


def line(ok, label, detail):
    print("  %-4s %-66s %s" % ("OK" if ok else "FAIL", label, detail))
    return ok


# ------------------------------------------------------------------ part A: the hole


def part_a():
    print("A. Section 9.4 overspend: root max_spend max 100, two children at 60, two gateways")
    res = []
    root = [{"key": "max_spend", "max": BUDGET}]
    a = mint_chain([{"key": "max_spend", "max": 60}], root, "child-a", "https://gw-a.example.com")
    b = mint_chain([{"key": "max_spend", "max": 60}], root, "child-b", "https://gw-b.example.com")
    va, vb = verify(a, "https://gw-a.example.com"), verify(b, "https://gw-b.example.com")
    res.append(line(va[0] == "accept" and vb[0] == "accept", "both chains verify (60 <= 100 on each edge)",
                    "gw-a=%s gw-b=%s" % (va[0], vb[0])))
    spent = 0
    for name, ch in (("gw-a", a), ("gw-b", b)):
        if 60 <= per_action_max(ch, "max_spend"):
            spent += 60
    res.append(line(spent == 120, "each gateway permits a 60 action under its per-action max",
                    "combined spend %d against a root ceiling of %d" % (spent, BUDGET)))
    over = mint_chain([{"key": "max_spend", "max": 120}], root, "child-c", "https://gw-a.example.com")
    vo = verify(over, "https://gw-a.example.com")
    res.append(line(vo[0] == "not_narrower", "a single child at 120 is caught at step 4", "%s %s" % vo))

    root2 = [{"key": "max_spend", "max": BUDGET}, {"key": "max_spend", "max_subtree": BUDGET}]
    a2 = mint_chain([{"key": "max_spend", "max": 60}, {"key": "max_spend", "max_subtree": 60}], root2, "child-a",
                    "https://gw-a.example.com")
    b2 = mint_chain([{"key": "max_spend", "max": 60}, {"key": "max_spend", "max_subtree": 60}], root2, "child-b",
                    "https://gw-b.example.com")
    v2 = (verify(a2, "https://gw-a.example.com")[0], verify(b2, "https://gw-b.example.com")[0])
    res.append(line(v2 == ("accept", "accept"), "with max_subtree 100 -> 60 + 60 both chains still verify",
                    "children's max_subtree sum 120 > 100; a chain-only verifier checks each edge only"))
    d = (step8(a2, 60, None), step8(b2, 60, None))
    res.append(line(d == (False, False), "step 8 at gateways that hold no subtree total (MUST deny)",
                    "gw-a permit=%s gw-b permit=%s, spend 0" % d))
    d = (step8(a2, 60, None, skip_cumulative=True), step8(b2, 60, None, skip_cumulative=True))
    res.append(line(d == (True, True), "gateways that skip the cumulative check",
                    "gw-a permit=%s gw-b permit=%s, spend 120" % d))
    return all(res)


# ------------------------------------------------------------------ part B: shared ledger


class AtomicLedger:
    """One ledger; check and debit are one operation under a lock."""

    def __init__(self, total):
        self.balance = total
        self.lock = threading.Lock()

    def authorize(self, amount):
        with self.lock:
            if amount <= self.balance:
                self.balance -= amount
                return True
            return False


class ReadThenDebitLedger:
    """Check at authorization, debit afterwards (the shape Section 9.4 says does not close the hole)."""

    def __init__(self, total, barrier):
        self.balance = total
        self.barrier = barrier

    def authorize(self, amount):
        ok = amount <= self.balance
        self.barrier.wait()  # force the interleaving: both gateways read before either debits
        if ok:
            self.balance -= amount
        return ok


def race(ledger_factory, trials, amount=60):
    totals = {}
    for _ in range(trials):
        ledger = ledger_factory()
        spent = []
        threads = [threading.Thread(target=lambda: spent.append(amount if ledger.authorize(amount) else 0))
                   for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        totals[sum(spent)] = totals.get(sum(spent), 0) + 1
    return totals


def part_b():
    print("B. Shared accounting: one ledger keyed by the root's subtree, balance 100")
    res = []
    t = race(lambda: AtomicLedger(BUDGET), 500)
    res.append(line(t == {60: 500}, "atomic check-and-debit, 2 gateways x 60, 500 races",
                    "combined spend per race: %s" % t))
    barrier_holder = {}

    def rtd():
        barrier_holder["b"] = threading.Barrier(2)
        return ReadThenDebitLedger(BUDGET, barrier_holder["b"])
    t = race(rtd, 50)
    res.append(line(t == {120: 50}, "read at authorization, debit afterwards (forced interleave)",
                    "combined spend per race: %s; balance ends at -20" % t))
    replicas = [AtomicLedger(BUDGET), AtomicLedger(BUDGET)]
    spent = sum(60 for r in replicas if r.authorize(60))
    res.append(line(spent == 120, "two uncoordinated writers (one replica per gateway)",
                    "combined spend %d" % spent))
    return all(res)


# ------------------------------------------------------------------ part C: allocator


class Allocator:
    """Single writer over a parent's budget."""

    def __init__(self, total):
        self.remaining = total
        self.allocations = {}

    def allocate(self, child, units):
        if units > self.remaining:
            return False
        self.remaining -= units
        self.allocations[child] = self.allocations.get(child, 0) + units
        return True


class Gateway:
    """Local enforcement against a balance; durable=True persists a debit before honoring."""

    def __init__(self, allocation, durable=True):
        self.balance = allocation
        self.store = allocation  # what survives a restart
        self.durable = durable
        self.pending = {}
        self.honored = 0

    def spend(self, amount):
        if amount > self.balance:
            return False
        self.balance -= amount
        if self.durable:
            self.store = self.balance
        self.honored += amount
        return True

    def restart(self):
        self.balance = self.store

    def reserve(self, action, amount):
        if amount > self.balance:
            return False
        self.balance -= amount
        self.pending[action] = amount
        return True

    def settle(self, action, consumed):
        """consumed: units the action actually used (0 if it did not complete)."""
        amount = self.pending.pop(action, None)
        if amount is None:  # reservation already released; the units were spent anyway
            self.honored += consumed
            return
        self.honored += consumed
        self.balance += amount - consumed

    def release_on_timeout(self, action):
        self.balance += self.pending.pop(action)


def part_c():
    print("C. Coordinated allocation with local enforcement (single-writer allocator, 100 units)")
    res = []
    al = Allocator(BUDGET)
    r = (al.allocate("child-a@gw-a", 60), al.allocate("child-b@gw-b", 60), al.allocate("child-b@gw-b", 40))
    res.append(line(r == (True, False, True) and al.remaining == 0,
                    "allocate 60 to A, then 60 to B refused, then 40 to B",
                    "results %s, parent remaining %d" % (r, al.remaining)))
    ga, gb = Gateway(60), Gateway(40)
    s = (ga.spend(60), ga.spend(1), gb.spend(40), gb.spend(1))
    res.append(line(s == (True, False, True, False) and ga.honored + gb.honored == 100,
                    "gw-a spends 60 then 1; gw-b spends 40 then 1",
                    "results %s, total honored %d" % (s, ga.honored + gb.honored)))

    # hazard 1: duplicate allocation
    al1, al2 = Allocator(BUDGET), Allocator(BUDGET)  # two issuers allocating offline from one budget
    dup = al1.allocate("child-a", 60) and al2.allocate("child-b", 60)
    res.append(line(dup, "hazard 1, duplicate allocation: two offline allocators, 60 + 60",
                    "both succeed; allocated %d > %d" % (60 + 60, BUDGET)))
    # hazard 2: local rollback
    g = Gateway(60, durable=False)
    g.spend(60)
    g.restart()  # restored from the pre-debit store
    again = g.spend(60)
    res.append(line(again and g.honored == 120, "hazard 2, local rollback: debit not persisted, gateway restarts",
                    "gw-a honors %d against an allocation of 60" % g.honored))
    g = Gateway(60, durable=True)
    g.spend(60)
    g.restart()
    res.append(line(not g.spend(60) and g.honored == 60, "  same with the debit persisted before honoring",
                    "second 60 refused; honored %d" % g.honored))
    # hazard 3: premature reuse
    g = Gateway(40)
    g.reserve("tx1", 40)
    g.release_on_timeout("tx1")  # unit returned before tx1 is settled
    g.spend(40)
    g.settle("tx1", consumed=40)  # tx1 turns out to have completed
    res.append(line(g.honored == 80, "hazard 3, premature reuse: reservation released before settlement",
                    "gw-b honors %d against an allocation of 40" % g.honored))
    g = Gateway(40)
    g.reserve("tx1", 40)
    blocked = not g.spend(40)
    g.settle("tx1", consumed=40)
    res.append(line(blocked and g.honored == 40, "  same with the reservation held until settled",
                    "second 40 refused while pending; honored %d" % g.honored))
    return all(res)


def self_test():
    print("self-test (the checks above must be able to fail):")
    res = []
    al = Allocator(BUDGET)
    res.append(line(al.allocate("a", 70) and not al.allocate("b", 40), "allocator refuses 70 + 40",
                    "remaining %d" % al.remaining))
    led = AtomicLedger(BUDGET)
    res.append(line(led.authorize(100) and not led.authorize(1), "atomic ledger refuses the 101st unit",
                    "balance %d" % led.balance))
    root = [{"key": "max_spend", "max": BUDGET}]
    a = mint_chain([{"key": "max_spend", "max": 60}], root, "child-a", "https://gw-a.example.com")
    tampered = a[:1] + [a[1][:-4] + ("AAAA" if not a[1].endswith("AAAA") else "BBBB")]
    res.append(line(verify(tampered, "https://gw-a.example.com")[0] == "signature_invalid",
                    "tampered child signature is rejected", verify(tampered, "https://gw-a.example.com")[0]))
    res.append(line(verify(a, "https://gw-b.example.com")[0] == "audience_mismatch",
                    "child-a chain at gw-b is rejected", verify(a, "https://gw-b.example.com")[0]))
    ok = all(res)
    print("self-test: %s" % ("PASS" if ok else "FAIL"))
    return ok


def main():
    print("python %s, cryptography %s" % (platform.python_version(), __import__("cryptography").__version__))
    ok = [part_a()]
    print()
    ok.append(part_b())
    print()
    ok.append(part_c())
    print()
    ok.append(self_test())
    print()
    print("lab2: %s" % ("PASS" if all(ok) else "FAIL"))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
