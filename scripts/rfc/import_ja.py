#!/usr/bin/env python3
"""Turn a translation written in the block format into data/rfc/<n>/ja.json.

The block format is what the translating model writes: one block per
paragraph or section title, keyed by the id from en.json.

  @@ title 4.2
  アクセストークンの要求
  @@ 4.2-1
  （段落の訳）

Only ids that exist in en.json are kept. Paragraphs of kind "pre" are never
translated and are rejected if present. The result records the source hash,
so a page can tell when the English text changed under a translation.

A translation written against an earlier en.json (positional ids, or a
parse that split paragraphs differently) is carried over with --map-from:
each old id is mapped to the current id of the paragraph with the same text.

Usage:
  import_ja.py 9449 translation.txt [--model NAME] [--map-from old-en.json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCK = re.compile(r"^@@ (title )?(\S+)[ \t]*$", re.M)


def parse_blocks(text: str) -> tuple[dict[str, str], dict[str, str]]:
    titles: dict[str, str] = {}
    paragraphs: dict[str, str] = {}
    text = text.replace("\r\n", "\n")
    matches = list(BLOCK.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end].strip()
        if not body:
            continue
        (titles if m.group(1) else paragraphs)[m.group(2)] = body
    return titles, paragraphs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("number", type=int)
    ap.add_argument("source", type=Path)
    ap.add_argument("--model", default="")
    ap.add_argument("--map-from", type=Path, help="the en.json the translation was written against")
    args = ap.parse_args()
    d = ROOT / "data" / "rfc" / str(args.number)
    en = json.loads((d / "en.json").read_text(encoding="utf-8"))
    kinds = {p["id"]: p["kind"] for s in en["sections"] for p in s["paragraphs"]}
    section_ids = {s["id"] for s in en["sections"]}
    titles, paragraphs = parse_blocks(args.source.read_text(encoding="utf-8"))

    if args.map_from:
        old = json.loads(args.map_from.read_text(encoding="utf-8"))
        norm = lambda t: re.sub(r"\s+", " ", t).strip()  # noqa: E731
        by_text = {(s["id"], norm(p["en"])): p["id"] for s in en["sections"] for p in s["paragraphs"]}
        old_text = {p["id"]: (s["id"], norm(p["en"])) for s in old["sections"] for p in s["paragraphs"]}
        mapped: dict[str, str] = {}
        unmapped = 0
        for k, v in paragraphs.items():
            new = by_text.get(old_text.get(k, ("", "")))
            if new:
                mapped[new] = v
            elif k in kinds:
                mapped[k] = v
            else:
                unmapped += 1
        print(f"  mapped {len(mapped)} paragraphs from the earlier parse; {unmapped} had no matching text and were dropped")
        paragraphs = mapped

    errors = [f"unknown paragraph id {k}" for k in paragraphs if k not in kinds]
    errors += [f"preformatted paragraph {k} must not be translated" for k in paragraphs if kinds.get(k) == "pre"]
    errors += [f"unknown section id {k}" for k in titles if k not in section_ids]
    for e in errors:
        print(f"  {e}", file=sys.stderr)
    paragraphs = {k: v for k, v in paragraphs.items() if kinds.get(k) in ("p", "li")}
    titles = {k: v for k, v in titles.items() if k in section_ids}
    wanted = [k for k, kind in kinds.items() if kind != "pre"]
    missing = [k for k in wanted if k not in paragraphs]
    if missing:
        print(f"  {len(missing)} of {len(wanted)} paragraphs untranslated: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}", file=sys.stderr)

    previous = {}
    if (d / "ja.json").exists():
        previous = json.loads((d / "ja.json").read_text(encoding="utf-8"))
    out = {
        "number": args.number,
        "source_hash": en["content_hash"],
        "translated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "model": args.model or previous.get("model", ""),
        "titles": {**previous.get("titles", {}), **titles},
        "paragraphs": {**previous.get("paragraphs", {}), **paragraphs},
    }
    (d / "ja.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"rfc{args.number}: {len(paragraphs)} paragraphs and {len(titles)} titles imported; {len(missing)} missing")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
