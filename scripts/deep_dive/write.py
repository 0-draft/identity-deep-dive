#!/usr/bin/env python3
"""Write a staged deep dive from Claude's structured output, plus a PR body.

Usage:
  write.py --work .deep-dive-work --result result.json --pr-body pr-body.md
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = REPO_ROOT / "templates" / "deep-dive"
FILES = {
    "readme": "README.md",
    "context": "context.md",
    "spec_notes": "spec-notes.md",
    "interop_checklist": "interop-checklist.md",
}
FENCE = re.compile(r"^\s*(```|~~~)")
TAG = re.compile(r"<(?=[A-Za-z/!?])")
SIGNATURE = re.compile(r"(generated (with|by)|co-authored-by)", re.IGNORECASE)
BARE_URL = re.compile(r"(?<![(<\[`])\bhttps?://[^\s)>\]`]+")
UNSAFE_LINK = re.compile(r"\]\(\s*(?!https?://|#|\./|\.\./|[A-Za-z0-9_.-]+\.md\b)[^)]*\)")


def clean(markdown: str) -> str:
    """Escape inline HTML and drop unsafe links outside code fences."""
    out, in_fence = [], False
    for line in markdown.replace("\r\n", "\n").split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line.rstrip())
            continue
        if not in_fence:
            if SIGNATURE.search(line):
                continue
            line = TAG.sub("&lt;", line)
            line = UNSAFE_LINK.sub("]", line)
            line = BARE_URL.sub(lambda m: f"<{m.group(0).rstrip('.,;:')}>{m.group(0)[len(m.group(0).rstrip('.,;:')):]}", line)
        out.append(line.rstrip())
    text = "\n".join(out).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    ap.add_argument("--pr-body", type=Path, required=True)
    args = ap.parse_args()

    subject = json.loads((args.work / "subject.json").read_text(encoding="utf-8"))
    raw = args.result.read_text(encoding="utf-8").strip()
    if not raw:
        raise SystemExit("write: Claude returned no structured output")
    result = json.loads(raw)
    for key in FILES:
        if not str(result.get(key, "")).strip():
            raise SystemExit(f"write: Claude output is missing {key}")

    target = REPO_ROOT / "tracks" / subject["track"] / "deep-dives" / subject["slug"]
    if target.exists():
        raise SystemExit(f"write: {target} already exists")
    target.mkdir(parents=True)
    for key, fname in FILES.items():
        (target / fname).write_text(clean(str(result[key])), encoding="utf-8")
    shutil.copy(TEMPLATE / "hands-on-log.md", target / "hands-on-log.md")

    one_liner = clean(str(result.get("one_liner", ""))).strip()
    unverified = [clean(str(u)).strip() for u in result.get("unverified", []) if str(u).strip()]
    rel = target.relative_to(REPO_ROOT)
    body = [
        f"Deep-dive draft for `{subject['name']}`{' revision ' + subject['rev'] if subject.get('rev') else ''} in `{subject['track']}`.",
        "",
        f"> {one_liner}",
        "",
        "## Why this subject",
        "",
        f"- Top candidate in `tracks/{subject['track']}/data/normalized/candidates.json` without a deep dive: `{subject['candidate']}`",
    ]
    if subject.get("ai_note"):
        body.append(f"- Triage note: {clean(subject['ai_note']).strip()}")
    body += [
        "",
        "## Files",
        "",
        *[f"- `{rel}/{f}`" for f in [*FILES.values(), "hands-on-log.md"]],
        "",
        "`hands-on-log.md` is the empty template: experiments are for a person to run.",
        "",
        "## Sources",
        "",
        f"- {subject['url']}",
        "",
        "## Check before merging",
        "",
        "Everything here was drafted from the source text alone. Read it against the source, fix what is wrong, and merge when it is something you would stand behind.",
        "",
    ]
    if unverified:
        body += ["Statements the drafter could not fully support from the material:", ""]
        body += [f"- [ ] {u}" for u in unverified] + [""]
    args.pr_body.write_text("\n".join(body), encoding="utf-8")
    print(f"write: {rel} ({len(FILES) + 1} files), {len(unverified)} unverified statement(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
