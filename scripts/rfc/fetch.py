#!/usr/bin/env python3
"""Fetch an RFC's plain text and split it into sections and paragraphs.

Output: data/rfc/<number>/en.json, the source side of the bilingual RFC
pages. Each paragraph carries a stable id (section number plus a hash of its
text), so a translation (ja.json, see import_ja.py) lines up with it
paragraph by paragraph and survives re-parsing. Preformatted blocks (examples, figures, ABNF) are kept verbatim
and marked "pre": they are shown on both sides and never translated.

Boilerplate that is the same in every RFC (status of this memo, copyright
notice, table of contents, authors' addresses) is dropped; the abstract,
every numbered section and the appendices are kept.

Usage:
  fetch.py 9449 [9126 ...]        write data/rfc/<n>/en.json
  fetch.py --stdin 9449 < rfc.txt parse a file instead of fetching
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "rfc"

HEADING = re.compile(r"^(\d+(?:\.\d+)*)\.\s{1,3}(\S.*)$")
APPENDIX = re.compile(r"^(?:Appendix\s+)?([A-Z](?:\.\d+)*)\.\s{1,3}(\S.*)$")
UNNUMBERED = {
    "Abstract",
    "Status of This Memo",
    "Copyright Notice",
    "Table of Contents",
    "Acknowledgements",
    "Acknowledgments",
    "Contributors",
    "Authors' Addresses",
    "Author's Address",
    "Index",
}
SKIP = {"Status of This Memo", "Copyright Notice", "Table of Contents", "Authors' Addresses", "Author's Address", "Index"}
FOOTER = re.compile(r"^\S.*\[Page \d+\]\s*$")
HEADER = re.compile(r"^RFC \d+\s{2,}.*\s{2,}\S+ \d{4}\s*$")
LIST_ITEM = re.compile(r"^\s{0,9}(?:[*o+-]|\d{1,2}\.|\(\d{1,2}\)|[a-z]\.|[ivx]+\.)\s+\S")
# A bibliography entry: a reference tag at the start of the block.
REFERENCE = re.compile(r"^\s*\[[A-Za-z0-9][A-Za-z0-9.\-_]*\](\s{2,}\S|\s*$)")


def fetch_text(number: int) -> str:
    import urllib.request

    req = urllib.request.Request(
        f"https://www.rfc-editor.org/rfc/rfc{number}.txt",
        headers={"User-Agent": "identity-deep-dive-rfc/0.1 (+https://github.com/0-draft/identity-deep-dive)"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def strip_pages(text: str) -> list[str]:
    """Lines without the running header and footer around each page break.
    A paragraph that runs over a page break is joined again: the break is
    dropped when the line before it does not end a sentence and the line
    after it continues at the same indent."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "\f" in line or FOOTER.match(line) or HEADER.match(line):
            # Everything from the footer to the header, with the blank lines
            # around them, is one page break (text saved from a browser has
            # no form feed, so the footer and header are matched on their own).
            while out and not out[-1].strip():
                out.pop()
            i += 1
            while i < len(lines) and (not lines[i].strip() or FOOTER.match(lines[i]) or HEADER.match(lines[i]) or "\f" in lines[i]):
                i += 1
            if i < len(lines) and out:
                prev, nxt = out[-1], lines[i]
                same_indent = (len(prev) - len(prev.lstrip())) == (len(nxt) - len(nxt.lstrip()))
                continues = not prev.rstrip().endswith((".", ":", ";", "!", "?")) and nxt.strip() and same_indent and not HEADING.match(nxt)
                if not continues:
                    out.append("")
            continue
        out.append(line.rstrip())
        i += 1
    return out


def title_of(lines: list[str]) -> str:
    """The centred title block: the run of centred lines (indented, and
    without the column gap of the header lines) just before "Abstract"."""
    for i, line in enumerate(lines):
        if line.strip() == "Abstract":
            block: list[str] = []
            for prev in reversed(lines[:i]):
                s = prev.strip()
                if not s:
                    if block:
                        break
                    continue
                indent = len(prev) - len(prev.lstrip())
                if indent >= 4 and "   " not in s:
                    block.insert(0, s)
                elif block:
                    break
            return " ".join(block)
    return ""


def looks_like_prose(block: list[str]) -> bool:
    """Wrapped sentences: several long lines, or one line ending a sentence,
    and nothing that only code starts a line with."""
    stripped = [l.strip() for l in block]
    if any(CODE_LINE.match(l) or l[:1] in "<>|" for l in stripped):
        return False
    long_lines = sum(1 for l in stripped if len(l) >= 45)
    if len(stripped) >= 2 and long_lines >= len(stripped) - 1:
        return True
    return len(stripped) == 1 and len(stripped[0]) >= 60 and stripped[0][-1] in ".:;)\""


CODE_LINE = re.compile(r"^\s*(HTTP/\d|GET |POST |PUT |DELETE |PATCH |Host:|Content-Type:|Authorization:|DPoP:|WWW-Authenticate:|Cache-Control:|Location:|[{}\[\]]\s*,?\s*$|\{\s*\"|\"[^\"]*\"\s*:|\.\.\.)")
LONG_TOKEN = re.compile(r"[A-Za-z0-9_\-=.+]{48,}")


def is_pre(block: list[str]) -> bool:
    """Examples, figures, ABNF, references: anything not set as body text.
    Body text sits at three spaces of indent; a list item starts there with
    its marker and may wrap deeper. Newer RFCs set examples at three spaces
    too, so lines that only code starts with (HTTP messages, JSON, long
    base64 runs) count as well."""
    first_indent = len(block[0]) - len(block[0].lstrip())
    if REFERENCE.match(block[0]):
        return True
    if LIST_ITEM.match(block[0]) and first_indent <= 9:
        return False
    if any(CODE_LINE.match(l) or LONG_TOKEN.search(l) for l in block):
        return True
    # ABNF: a rule definition with ABNF operators or core rules.
    if re.match(r"^\s*[A-Za-z][A-Za-z0-9-]*\s*=/?\s", block[0]) and re.search(r"%x|\bALPHA\b|\bDIGIT\b|\bVCHAR\b|\d\*|\*\(|\*\d", "\n".join(block)):
        return True
    # A term on its own line with its definition indented under it, as in
    # parameter lists: body text, not an example.
    head = block[0].strip()
    if len(block) >= 2 and len(head) <= 40 and not head.endswith("."):
        definition = " ".join(l.strip() for l in block[1:])
        if definition.endswith((".", ":", ";")) and (looks_like_prose(block[1:]) or len(head.split()) <= 3):
            return False
    text = "\n".join(block)
    if re.search(r"(\+--|--\+|\|\s{2,}|<-{2,}|-{2,}>|^\s*[{}\[\]]\s*$)", text, re.M):
        return True
    if re.match(r"^\s*(Figure|Table) \d+:", block[0]):
        return True
    if first_indent >= 4:
        return not looks_like_prose(block)
    return any(len(l) - len(l.lstrip()) >= 8 for l in block)


def parse(text: str, number: int) -> dict:
    lines = strip_pages(text)
    title = title_of(lines)
    sections: list[dict] = []
    current: dict | None = None
    block: list[str] = []
    counter = 0

    def flush() -> None:
        nonlocal block, counter
        if not block or current is None:
            block = []
            return
        # Consecutive list items without a blank line between them are one
        # block in the text; each item is its own paragraph here.
        if LIST_ITEM.match(block[0]) and not is_pre(block):
            indent = len(block[0]) - len(block[0].lstrip())
            parts: list[list[str]] = [[block[0]]]
            for line in block[1:]:
                if LIST_ITEM.match(line) and len(line) - len(line.lstrip()) == indent:
                    parts.append([line])
                else:
                    parts[-1].append(line)
            for part in parts:
                block = part
                flush_one()
            block = []
            return
        flush_one()

    def flush_one() -> None:
        nonlocal block, counter
        counter += 1
        if is_pre(block):
            kind, en = "pre", "\n".join(block)
        elif LIST_ITEM.match(block[0]):
            kind, en = "li", " ".join(l.strip() for l in block)
        else:
            kind, en = "p", " ".join(l.strip() for l in block)
        # The id names the section and the text, not the position, so a
        # translation keyed by it survives the parser splitting or joining
        # neighbouring paragraphs; only a paragraph whose text changed needs
        # translating again.
        pid = f"{current['id']}-{paragraph_hash(en)}"
        # Identical text twice in one section (repeated registry lines):
        # the second gets a suffix, and shares the first one's translation.
        taken = {p["id"] for p in current["paragraphs"]}
        base, n = pid, 2
        while pid in taken:
            pid = f"{base}-{n}"
            n += 1
        current["paragraphs"].append({"id": pid, "kind": kind, "en": en})
        block = []

    def start(sid: str, stitle: str) -> None:
        nonlocal current, counter
        flush()
        counter = 0
        current = {"id": sid, "title": stitle, "paragraphs": []}
        sections.append(current)

    heading_indent = -1
    for n, line in enumerate(lines):
        s = line.strip()
        if not s:
            heading_indent = -1
            flush()
            continue
        # A heading too long for one line continues on the next, indented to
        # where its title started, and a blank line follows.
        if heading_indent >= 0 and current is not None and not block:
            indent = len(line) - len(line.lstrip())
            nxt = lines[n + 1].strip() if n + 1 < len(lines) else ""
            if indent == heading_indent and not nxt:
                current["title"] += " " + s
                heading_indent = -1
                continue
        heading_indent = -1
        if not line.startswith(" "):
            m = HEADING.match(line) or APPENDIX.match(line)
            if m:
                start(m.group(1), m.group(2).strip())
                heading_indent = len(line) - len(m.group(2))
                continue
            if s in UNNUMBERED:
                if s in SKIP:
                    flush()
                    current = None
                    continue
                start(s.lower().replace("'", "").replace(" ", "-"), s)
                continue
            # The first page's header lines (stream, authors, date) are not
            # inside a section and are dropped with everything before the
            # abstract.
            if current is None:
                continue
        if current is None:
            continue
        block.append(line)
    flush()
    return {
        "number": number,
        "title": title,
        "url": f"https://www.rfc-editor.org/rfc/rfc{number}",
        "fetched_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "sections": sections,
    }


def paragraph_hash(en: str) -> str:
    return hashlib.sha1(re.sub(r"\s+", " ", en).strip().encode()).hexdigest()[:8]


def content_hash(doc: dict) -> str:
    """Hash of the English paragraphs only, so a translation can say which
    source text it belongs to (fetch time and title excluded)."""
    h = hashlib.sha256()
    for sec in doc["sections"]:
        for p in sec["paragraphs"]:
            h.update(p["id"].encode())
            h.update(b"\0")
            h.update(p["en"].encode())
            h.update(b"\n")
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("numbers", nargs="+", type=int)
    ap.add_argument("--stdin", action="store_true", help="parse the RFC text from stdin (one number only)")
    args = ap.parse_args()
    for n in args.numbers:
        text = sys.stdin.read() if args.stdin else fetch_text(n)
        doc = parse(text, n)
        doc["content_hash"] = content_hash(doc)
        d = OUT / str(n)
        d.mkdir(parents=True, exist_ok=True)
        (d / "en.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        paras = sum(len(s["paragraphs"]) for s in doc["sections"])
        pre = sum(1 for s in doc["sections"] for p in s["paragraphs"] if p["kind"] == "pre")
        print(f"rfc{n}: {doc['title']!r}: {len(doc['sections'])} sections, {paras} paragraphs ({pre} preformatted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
