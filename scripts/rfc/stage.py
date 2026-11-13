#!/usr/bin/env python3
"""Stage an RFC for translation: cut its translatable paragraphs into chunks
a model can translate in one pass each.

Reads data/rfc/<n>/en.json (fetch.py writes it) and writes, under --out:

  plan.json          {"number": n, "title": ..., "chunks": ["00", "01", ...]}
  chunks/<k>.json    the paragraphs of one chunk: section titles and the
                     "p"/"li" paragraphs, in document order, with their ids

Paragraphs already translated in ja.json are skipped unless --all is given,
so a re-run after a partial result only translates what is missing.

Usage:
  stage.py --number 9449 --out rfc-work [--chunk-words 2500] [--all]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--number", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--chunk-words", type=int, default=2500)
    ap.add_argument("--all", action="store_true", help="retranslate paragraphs that already have a translation")
    args = ap.parse_args()

    d = ROOT / "data" / "rfc" / str(args.number)
    en = json.loads((d / "en.json").read_text(encoding="utf-8"))
    done: set[str] = set()
    done_titles: set[str] = set()
    ja_path = d / "ja.json"
    if ja_path.exists() and not args.all:
        ja = json.loads(ja_path.read_text(encoding="utf-8"))
        if ja.get("source_hash") == en.get("content_hash"):
            done = set(ja.get("paragraphs", {}))
            done_titles = set(ja.get("titles", {}))

    items: list[dict] = []
    for sec in en["sections"]:
        if sec["id"] not in done_titles:
            items.append({"id": sec["id"], "kind": "title", "en": sec["title"]})
        for p in sec["paragraphs"]:
            if p["kind"] == "pre" or p["id"] in done:
                continue
            items.append({"id": p["id"], "kind": p["kind"], "en": p["en"]})

    chunks: list[list[dict]] = []
    cur: list[dict] = []
    words = 0
    for it in items:
        n = len(it["en"].split())
        if cur and words + n > args.chunk_words:
            chunks.append(cur)
            cur, words = [], 0
        cur.append(it)
        words += n
    if cur:
        chunks.append(cur)

    out = args.out
    (out / "chunks").mkdir(parents=True, exist_ok=True)
    keys = []
    for i, chunk in enumerate(chunks):
        key = f"{i:02d}"
        keys.append(key)
        (out / "chunks" / f"{key}.json").write_text(
            json.dumps({"number": args.number, "title": en["title"], "items": chunk}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    (out / "plan.json").write_text(json.dumps({"number": args.number, "title": en["title"], "chunks": keys}) + "\n", encoding="utf-8")
    print(f"rfc{args.number}: {len(items)} items to translate in {len(chunks)} chunks ({len(done)} paragraphs already done)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
