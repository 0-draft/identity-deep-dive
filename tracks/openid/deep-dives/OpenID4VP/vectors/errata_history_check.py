"""Check that the OpenID4VP 1.0 errata Document History covers every normative change.

Usage:
  python3 -I errata_history_check.py REPO [BASE] [HEAD] [PRS_JSON]
  python3 -I errata_history_check.py --self-test

REPO is a clone of https://github.com/openid/OpenID4VP. BASE defaults to the tag
1.0-final, HEAD to main. PRS_JSON is optional output of
  gh pr list -R openid/OpenID4VP --state merged --limit 400 --json number,title,mergeCommit
and maps a merge commit to its pull request number; without it the number is read
from the commit subject.

No rendering (mmark/xml2rfc) is involved. The script reads the markdown source,
drops the front matter, fenced code blocks and the Document History, splits the
text into sections (keyed by heading anchor or title) and sentences, normalizes
whitespace, and treats a sentence that contains an RFC 2119 keyword in capitals
as normative. It then compares:

  1. BASE against HEAD as a whole (normative sentences added, removed, changed,
     or moved to another section, which can change their scope),
  2. each first-parent commit between BASE and HEAD that touched the 1.0 text or
     its examples against its parent, to attribute every change to a pull
     request, and to see which Document History bullets that pull request added.

Status per pull request:
  NO HISTORY ENTRY       a normative sentence changed, no bullet was added
  HISTORY, PROSE CHANGE  a bullet was added, only sentences without a keyword changed
  HISTORY ONLY           a bullet was added, no sentence changed at all
All of these still need a human reading: a sentence without a keyword can change
behaviour, and one bullet can cover only part of a pull request.
"""
import difflib
import json
import re
import subprocess
import sys
from collections import Counter

PATHS = ["1.0/openid-4-verifiable-presentations-1_0.md", "openid-4-verifiable-presentations-1_0.md"]
KEYWORDS = re.compile(r"\b(MUST NOT|MUST|REQUIRED|SHALL NOT|SHALL|SHOULD NOT|SHOULD|NOT RECOMMENDED|RECOMMENDED|MAY|OPTIONAL)\b")
HEADING = re.compile(r"^(\.?#+)\s+(.*?)\s*(\{#([^}]+)\})?\s*$")
NEW_UNIT = re.compile(r"^\s*([*+-]|\d+\.)\s+")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`*\[(\"])")
PAIR_RATIO = 0.5


def only_normative(secs):
    return {k: [s for s in v if KEYWORDS.search(s)] for k, v in secs.items() if any(KEYWORDS.search(s) for s in v)}


def keywords(s):
    return Counter(m.replace("SHALL", "MUST") for m in KEYWORDS.findall(s))


def parse(text):
    """Return ({section: [sentences]}, [(revision, bullet) in the Document History])."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "%%%":
        end = lines.index("%%%", 1)
        lines = lines[end + 1:]
    sections, history = {}, []
    section, units, cur = "(preamble)", [], []
    in_fence = in_history = False
    rev = None

    def flush():
        if cur:
            units.append(" ".join(cur))
            cur.clear()

    def close_section():
        flush()
        sents = []
        for u in units:
            u = re.sub(r"\s+", " ", u).strip()
            carry = ""
            for s in SENTENCE_END.split(u):
                s = (carry + " " + s).strip() if carry else s.strip()
                if len(s.split()) < 5:  # "`x`: : OPTIONAL." stays with the sentence after it
                    carry = s
                    continue
                carry = ""
                sents.append(s)
            if carry:
                sents.append(carry)
        sections.setdefault(section, []).extend(sents)
        units.clear()

    for line in lines:
        if in_history:
            if re.match(r"^-(\d+|final)\s*$", line):
                rev = line.strip()
            elif rev and re.match(r"^\s*\*\s+", line):
                history.append((rev, re.sub(r"\s+", " ", re.sub(r"^\s*\*\s+", "", line)).strip()))
            continue
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            flush()
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            close_section()
            title = m.group(2).strip()
            if title == "Document History":
                in_history = True
                continue
            section = m.group(4) or title
            continue
        if not line.strip() or line.strip().startswith("{") or line.lstrip().startswith("<{{"):
            flush()
            continue
        if NEW_UNIT.match(line) or line.lstrip().startswith("|"):
            flush()
        cur.append(line.strip())
    close_section()
    return {k: v for k, v in sections.items() if v}, history


def diff(old, new):
    """Compare two section maps. Returns lists of (kind, section, old, new)."""
    out = []
    removed, added = [], []
    for sec in list(old) + [s for s in new if s not in old]:
        o, n = Counter(old.get(sec, [])), Counter(new.get(sec, []))
        removed += [(sec, s) for s in (o - n).elements()]
        added += [(sec, s) for s in (n - o).elements()]
    # a sentence that only moved to another section is not a change
    for r in list(removed):
        hit = next((a for a in added if a[1] == r[1]), None)
        if hit:
            removed.remove(r)
            added.remove(hit)
            out.append(("moved", f"{r[0]} -> {hit[0]}", r[1], hit[1]))
    # pair the rest as changed when they are similar enough, best match first
    cands = sorted(((difflib.SequenceMatcher(None, r[1], a[1]).ratio(), i, j)
                    for i, r in enumerate(removed) for j, a in enumerate(added)), reverse=True)
    used_r, used_a = set(), set()
    for ratio, i, j in cands:
        if ratio < PAIR_RATIO:
            break
        if i in used_r or j in used_a:
            continue
        used_r.add(i)
        used_a.add(j)
        r, a = removed[i], added[j]
        kind = "changed-keywords" if keywords(r[1]) != keywords(a[1]) else "changed-wording"
        out.append((kind, a[0], r[1], a[1]))
    out += [("removed", r[0], r[1], None) for i, r in enumerate(removed) if i not in used_r]
    out += [("added", a[0], None, a[1]) for j, a in enumerate(added) if j not in used_a]
    return out


def normative(changes):
    return [c for c in changes if c[0] != "moved"]


def has_kw(c):
    return any(x is not None and KEYWORDS.search(x) for x in (c[2], c[3]))


def classify(before_text, after_text):
    """Compare two versions of the text. Returns (status, normative, prose, history added, history removed)."""
    before, before_hist = parse(before_text)
    after, after_hist = parse(after_text)
    # a keyword sentence that moved to another section counts: the move can change its scope
    norm = diff(only_normative(before), only_normative(after))
    prose = [c for c in normative(diff(before, after)) if not has_kw(c)]
    h_add = [b for b in after_hist if b not in before_hist]
    h_del = [b for b in before_hist if b not in after_hist]
    if norm:
        status = "ok" if h_add else "NO HISTORY ENTRY"
    elif h_add:
        status = "HISTORY, PROSE CHANGE" if prose else "HISTORY ONLY"
    else:
        status = "no normative change, no history entry"
    return status, norm, prose, h_add, h_del


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, text=True).stdout


def file_at(repo, rev):
    for p in PATHS:
        try:
            return git(repo, "show", f"{rev}:{p}")
        except subprocess.CalledProcessError:
            pass
    raise SystemExit(f"no 1.0 text at {rev}")


def show(c, indent="    ", tag=""):
    kind, sec, o, n = c
    kw = lambda s: ",".join(sorted(keywords(s).elements())) if s else ""
    lines = [f"{indent}[{tag}{kind}] {sec}"]
    if o is not None:
        lines.append(f"{indent}  - ({kw(o)}) {o}")
    if n is not None:
        lines.append(f"{indent}  + ({kw(n)}) {n}")
    return "\n".join(lines)


def run(repo, base, head, prs_json):
    pr_by_commit = {}
    if prs_json:
        for p in json.load(open(prs_json, encoding="utf-8")):
            if p.get("mergeCommit"):
                pr_by_commit[p["mergeCommit"]["oid"]] = p["number"]
    head_sha = git(repo, "rev-parse", head).strip()
    base_sha = git(repo, "rev-parse", f"{base}^{{commit}}").strip()
    print(f"repo: openid/OpenID4VP\nbase: {base} = {base_sha}\nhead: {head} = {head_sha}")
    print(f"head date: {git(repo, 'log', '-1', '--format=%cI', head_sha).strip()}\n")

    old_secs, _ = parse(file_at(repo, base_sha))
    new_secs, head_history = parse(file_at(repo, head_sha))
    total = diff(only_normative(old_secs), only_normative(new_secs))
    n_old = sum(map(len, only_normative(old_secs).values()))
    n_new = sum(map(len, only_normative(new_secs).values()))
    print(f"normative sentences: base {n_old}, head {n_new}")
    newest = head_history[0][0] if head_history else None
    print(f"head Document History bullets under {newest}: {sum(1 for r, _ in head_history if r == newest)}")
    kinds = Counter(c[0] for c in total)
    print("BASE..HEAD: " + ", ".join(f"{k} {kinds[k]}" for k in
          ("added", "removed", "changed-keywords", "changed-wording", "moved")) + "\n")

    rows = git(repo, "log", "--first-parent", "--reverse", "--format=%H%x09%ad%x09%s", "--date=short",
               f"{base_sha}..{head_sha}", "--", *PATHS, "1.0/examples", "examples").strip().split("\n")
    rows = list(dict.fromkeys(rows))
    first_seen = {}  # sentence text -> pr label where it first appeared/disappeared
    flags = {}
    print("== per pull request (first-parent order)")
    for row in rows:
        sha, date, subject = row.split("\t")
        m = re.search(r"#(\d+)", subject)
        pr = pr_by_commit.get(sha) or (int(m.group(1)) if m else None)
        label = f"#{pr}" if pr else sha[:7]
        status, norm, prose, h_add, h_del = classify(file_at(repo, sha + "^"), file_at(repo, sha))
        examples = [f for f in git(repo, "diff", "--name-only", sha + "^", sha).split()
                    if f.startswith(("1.0/examples/", "examples/"))]
        for c in norm:
            for x in (c[2], c[3]):
                if x is not None:
                    first_seen.setdefault(x, label)
        flags.setdefault(status, []).append(label)
        print(f"{label} {sha[:7]} {date} {subject}")
        print(f"  normative: {len(norm)}; prose without keyword: {len(prose)}; example files: {len(examples)};"
              f" history added: {len(h_add)}, removed: {len(h_del)} -> {status}")
        for b in h_add:
            print(f"    history+ [{b[0]}] {b[1]}")
        for b in h_del:
            print(f"    history- [{b[0]}] {b[1]}")
        for c in norm:
            print(show(c))
        for c in prose:
            print(show(c, tag="prose "))
        for f in examples:
            print(f"    example: {f}")
    print()
    print("== BASE..HEAD normative changes, attributed to the pull request that first touched the sentence")
    for c in total:
        src = sorted({first_seen.get(x, "?") for x in (c[2], c[3]) if x is not None})
        print(show(c, indent="  ") + f"\n      by: {' '.join(src)}")
    print()
    for status in ("NO HISTORY ENTRY", "HISTORY, PROSE CHANGE", "HISTORY ONLY",
                   "no normative change, no history entry", "ok"):
        print(f"{status}: {' '.join(flags.get(status, [])) or 'none'}")


SELF_OLD = """%%%
title = "t"
%%%

# Intro

This section has text without any keywords.

## Request {#req}

The Wallet MUST check the `nonce`. The Verifier MAY send `state`.

* `foo`: OPTIONAL. A value.

```
example MUST be ignored here
```

# Document History

-02

   * first change

-01

   * old
"""


def self_test():
    """Feed altered copies through classify() and check each gets the expected status."""
    hist = lambda t, b: t.replace("   * first change", "   * first change\n   * " + b)
    cases = [
        ("whitespace only", SELF_OLD.replace("MUST check the", "MUST   check\nthe"),
         "no normative change, no history entry"),
        ("change inside a code block", SELF_OLD.replace("example MUST", "example SHOULD"),
         "no normative change, no history entry"),
        ("keyword MAY -> SHOULD, no history", SELF_OLD.replace("Verifier MAY", "Verifier SHOULD"), "NO HISTORY ENTRY"),
        ("OPTIONAL -> RECOMMENDED with history",
         hist(SELF_OLD.replace("OPTIONAL. A value.", "RECOMMENDED. A value."), "foo is recommended"), "ok"),
        ("new MUST sentence, no history",
         SELF_OLD.replace("send `state`.", "send `state`. The Wallet MUST NOT follow redirects."), "NO HISTORY ENTRY"),
        ("history bullet only", hist(SELF_OLD, "editorial"), "HISTORY ONLY"),
        ("prose sentence without keyword, with history",
         hist(SELF_OLD.replace("A value.", "A value. If absent, nothing is implied by the Verifier."), "absent foo"),
         "HISTORY, PROSE CHANGE"),
        ("keyword sentence moved to another section, no history",
         SELF_OLD.replace("without any keywords.", "without any keywords. The Wallet MUST check the `nonce`.")
         .replace("The Wallet MUST check the `nonce`. The Verifier", "The Verifier"),
         "NO HISTORY ENTRY"),
        ("sentences reordered inside a section",
         SELF_OLD.replace("The Wallet MUST check the `nonce`. The Verifier MAY send `state`.",
                          "The Verifier MAY send `state`. The Wallet MUST check the `nonce`."),
         "no normative change, no history entry"),
    ]
    fails = 0
    for name, text, want in cases:
        status, norm, prose, h_add, _ = classify(SELF_OLD, text)
        ok = status == want
        fails += not ok
        print(f"  {name}: {status} (normative {len(norm)}, prose {len(prose)}, history+ {len(h_add)})"
              f" -> {'pass' if ok else 'FAIL, expected ' + want}")
    print(f"self-test: {len(cases) - fails}/{len(cases)} pass")
    return fails == 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(0 if self_test() else 1)
    if not 2 <= len(sys.argv) <= 5:
        sys.exit(__doc__)
    a = sys.argv[1:] + [None] * 4
    run(a[0], a[1] or "1.0-final", a[2] or "main", a[3])
    print("\nself-test:")
    sys.exit(0 if self_test() else 1)
