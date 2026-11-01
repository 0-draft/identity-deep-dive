#!/usr/bin/env python3
"""Validate the synthesis output and write data/synthesis.json.

Same rules as the insight pass: ids and member names must be ones that were
staged, text is escaped, and nothing from the model becomes a URL or a path.
Without a usable result the previous file is kept as it is.

Usage:
  apply.py --work synthesis-work --result synthesis-work/result.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "insights"))
from guard import REFUSED_MARKER, contains_secret  # noqa: E402
from tracks import TRACKS  # noqa: E402

TOPIC_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,48}")
OUT = REPO_ROOT / "data" / "synthesis.json"


def text(value: object, limit: int) -> str:
    s = re.sub(r"\s+", " ", str(value or "")).strip()[:limit]
    # Rendered by Astro, which escapes on output; still keep it plain.
    return s.replace("<", "‹").replace(">", "›")


def validate(result: dict, allowed: dict) -> tuple[dict, list[str]]:
    warnings: list[str] = []
    ids = set(allowed.get("insight_ids", []))
    names = {t: set(v) for t, v in allowed.get("members", {}).items()}

    picks, seen = [], set()
    for p in result.get("picks", [])[:5]:
        pid = p.get("id")
        if pid not in ids or pid in seen:
            warnings.append(f"dropped pick {str(pid)[:80]}")
            continue
        seen.add(pid)
        picks.append({"id": pid, "why": text(p.get("why"), 280), "why_ja": text(p.get("why_ja"), 280)})

    topics, topic_ids = [], set()
    for t in result.get("topics", [])[:12]:
        tid = str(t.get("id", ""))
        if not TOPIC_ID.fullmatch(tid) or tid in topic_ids:
            warnings.append(f"dropped topic {tid[:60]}")
            continue
        members = []
        for m in t.get("members", [])[:30]:
            track, name = m.get("track"), m.get("name")
            if track in TRACKS and name in names.get(track, set()):
                if {"track": track, "name": name} not in members:
                    members.append({"track": track, "name": name})
            else:
                warnings.append(f"dropped member {track}/{str(name)[:60]} of {tid}")
        if not members:
            warnings.append(f"dropped empty topic {tid}")
            continue
        topic_ids.add(tid)
        topics.append(
            {
                "id": tid,
                "name": text(t.get("name"), 60),
                "name_ja": text(t.get("name_ja"), 60),
                "summary": text(t.get("summary"), 400),
                "summary_ja": text(t.get("summary_ja"), 400),
                "members": members,
                "related": [str(r) for r in t.get("related", [])[:6]],
            }
        )
    for t in topics:
        t["related"] = [r for r in t["related"] if r in topic_ids and r != t["id"]]
    return {"picks": picks, "topics": topics}, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    args = ap.parse_args()

    if (args.result.parent / REFUSED_MARKER).exists():
        print("::error::synthesis: output was discarded by guard.py; keeping the previous synthesis")
        return 1
    raw = args.result.read_text(encoding="utf-8").strip() if args.result.exists() else ""
    if not raw:
        print("synthesis: no result; keeping the previous synthesis")
        return 0
    if contains_secret(raw):
        print("::error::synthesis: output contains a credential-shaped string; keeping the previous synthesis")
        return 1
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"::warning::synthesis: output is not JSON ({exc}); keeping the previous synthesis")
        return 0
    allowed = json.loads((args.work / "allowed.json").read_text(encoding="utf-8"))
    data, warnings = validate(result, allowed)
    for w in warnings:
        print(f"::warning::synthesis: {w}")
    data["generated_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"synthesis: {len(data['picks'])} pick(s), {len(data['topics'])} topic(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
