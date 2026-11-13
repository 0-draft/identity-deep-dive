#!/usr/bin/env python3
"""Fetch an RFC's plain text and split it into sections and paragraphs.

Output: data/rfc/<number>/en.json, the source side of the bilingual RFC
pages. Each paragraph carries a stable id (section number plus index), so a
translation (ja.json, see import_ja.py) lines up with it paragraph by
paragraph. Preformatted blocks (examples, figures, ABNF) are kept verbatim
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
LIST_ITEM = re.compile(r"^\s{0,6}(?:[*o+-]|\d{1,2}\.|\(\d{1,2}\)|[a-z]\.|[ivx]+\.)\s+\S")


def fetch_text(number: int) -> str:
    import urllib.request

    req = urllib.request.Request(
        f"https://www.rfc-editor.org/rfc/rfc{number}.txt",
        headers={"User-Agent": "identity-deep-dive-rfc/0.1 (+https://github.com/0-draft/identity-deep-dive)"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def strip_pages(text: str) -> list[str]:
    """Lines without the running header and footer around each page break."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "\f" in line:
            # Footer precedes the form feed, the header follows it; both may
            # be separated from it by blank lines.
            while out and (not out[-1].strip() or FOOTER.match(out[-1])):
                out.pop()
            i += 1
            while i < len(lines) and (not lines[i].strip() or HEADER.match(lines[i])):
                i += 1
            out.append("")
            continue
        # Text saved from a browser loses the form feed, so the running
        # header and footer are also dropped on their own.
        if FOOTER.match(line) or HEADER.match(line):
            while out and not out[-1].strip():
                out.pop()
            out.append("")
            i += 1
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


def is_pre(block: list[str]) -> bool:
    if any(len(l) - len(l.lstrip()) >= 8 for l in block):
        return True
    text = "\n".join(block)
    if re.search(r"(\+--|--\+|\|\s{2,}|<-{2,}|-{2,}>|^\s*[{}\[\]]\s*$)", text, re.M):
        return True
    # Caption lines of figures and tables stay with the figure.
    return bool(re.match(r"^\s*(Figure|Table) \d+:", block[0]))


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
        counter += 1
        pid = f"{current['id']}-{counter}"
        if is_pre(block):
            current["paragraphs"].append({"id": pid, "kind": "pre", "en": "\n".join(block)})
        elif LIST_ITEM.match(block[0]):
            current["paragraphs"].append({"id": pid, "kind": "li", "en": " ".join(l.strip() for l in block)})
        else:
            current["paragraphs"].append({"id": pid, "kind": "p", "en": " ".join(l.strip() for l in block)})
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
