#!/usr/bin/env python3
"""Check the spec explainers in data/specs against their template.

For every data/specs/<id>/README.md (and README.ja.md when present):
  - the id is a spec on the map (data/landscape.json)
  - the H1 and the one-line quote are there
  - the sections are the template's, in order
  - there are at least two mermaid diagrams, and every fence is closed
  - every link under Sources points at an official host
  - every "(Section X)" reference in the body also appears in Sources,
    as a section number in a link text or fragment
  - the Japanese edition has the same sections, the same number of
    diagrams and the same section references as the English

Exit status 1 on any problem. Used by the PR check and locally:
  python3 scripts/landscape/explainers.py [--ids dpop,par]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "data" / "specs"

SECTIONS = {
    "en": ["When you reach for it", "The problem it solves", "How it works", "What the spec requires", "Watch out", "Sources"],
    "ja": ["どういうときに使うか", "解決する問題", "仕組み", "仕様が求めること", "注意点", "出典"],
}
ONE_LINE = {"en": re.compile(r"^>\s*In one line:\s*\S", re.M), "ja": re.compile(r"^>\s*一言で言うと[:：]\s*\S", re.M)}
OFFICIAL = re.compile(
    r"^https://("
    r"(www\.)?rfc-editor\.org|datatracker\.ietf\.org|(www\.)?ietf\.org|openid\.net|spiffe\.io|"
    r"github\.com/spiffe/spiffe|raw\.githubusercontent\.com/spiffe/spiffe|github\.com/openid/"
    r")"
)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\n]*)$", re.M)
SECTION_REF = re.compile(r"\(Section\s+([A-Z]?\d+(?:\.\d+)*)\)|\(Sections?\s+([A-Z]?\d+(?:\.\d+)*)(?:\s*(?:,|and|to|-)\s*[A-Z]?\d+(?:\.\d+)*)*\)")
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def sections_of(md: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", md, re.M)]


def fences(md: str) -> tuple[int, int]:
    """(mermaid fences, unclosed fences)."""
    mermaid = 0
    open_run: str | None = None
    unclosed = 0
    for m in FENCE.finditer(md):
        run, info = m.group(1), m.group(2).strip()
        if open_run is None:
            open_run = run
            if info.startswith("mermaid"):
                mermaid += 1
        elif run[0] == open_run[0] and len(run) >= len(open_run):
            open_run = None
    if open_run is not None:
        unclosed = 1
    return mermaid, unclosed


def section_refs(md: str) -> set[str]:
    refs: set[str] = set()
    for m in re.finditer(r"\(Sections?\s+([^)]+)\)", md):
        for n in re.findall(r"[A-Z]?\d+(?:\.\d+)*", m.group(1)):
            refs.add(n)
    return refs


def sources_block(md: str, lang: str) -> str:
    name = SECTIONS[lang][-1]
    m = re.search(rf"^##\s+{re.escape(name)}\s*$", md, re.M)
    return md[m.end():] if m else ""


def check(md: str, lang: str, label: str) -> list[str]:
    errs: list[str] = []
    if not re.search(r"^#\s+\S", md, re.M):
        errs.append(f"{label}: no H1")
    if not ONE_LINE[lang].search(md):
        errs.append(f"{label}: no one-line quote")
    got = sections_of(md)
    if got != SECTIONS[lang]:
        errs.append(f"{label}: sections are {got}, expected {SECTIONS[lang]}")
    mermaid, unclosed = fences(md)
    if mermaid < 2:
        errs.append(f"{label}: {mermaid} mermaid diagram(s), expected at least 2")
    if unclosed:
        errs.append(f"{label}: unclosed code fence")
    src = sources_block(md, lang)
    links = LINK.findall(src)
    if not links:
        errs.append(f"{label}: no links under Sources")
    for text, url in links:
        if not OFFICIAL.match(url):
            errs.append(f"{label}: non-official source {url}")
    cited = section_refs(md.split(f"## {SECTIONS[lang][-1]}")[0])
    covered = {n for text, url in links for n in re.findall(r"[A-Z]?\d+(?:\.\d+)*", text + " " + url.split("#")[-1])}
    missing = sorted(n for n in cited if n not in covered)
    if missing:
        errs.append(f"{label}: sections cited but not in Sources: {', '.join(missing)}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="", help="comma-separated spec ids to check (default: all)")
    args = ap.parse_args()
    on_map = {s["id"] for s in json.loads((ROOT / "data" / "landscape.json").read_text(encoding="utf-8"))["specs"]}
    wanted = set(filter(None, args.ids.split(","))) if args.ids else None
    errs: list[str] = []
    count = 0
    for d in sorted(SPECS.iterdir()) if SPECS.exists() else []:
        if not d.is_dir() or (wanted and d.name not in wanted):
            continue
        if d.name not in on_map:
            errs.append(f"{d.name}: not a spec on the map")
            continue
        en_p, ja_p = d / "README.md", d / "README.ja.md"
        if not en_p.exists():
            errs.append(f"{d.name}: no README.md")
            continue
        count += 1
        en = en_p.read_text(encoding="utf-8")
        errs += check(en, "en", f"{d.name}/README.md")
        if ja_p.exists():
            ja = ja_p.read_text(encoding="utf-8")
            errs += check(ja, "ja", f"{d.name}/README.ja.md")
            if fences(ja)[0] != fences(en)[0]:
                errs.append(f"{d.name}: diagram count differs between editions")
            en_refs, ja_refs = section_refs(en), section_refs(ja)
            if en_refs != ja_refs:
                errs.append(f"{d.name}: section references differ: en-only {sorted(en_refs - ja_refs)}, ja-only {sorted(ja_refs - en_refs)}")
    for e in errs:
        print(f"  {e}")
    print(f"explainers: {count} checked, {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
