#!/usr/bin/env python3
"""Refuse model output that carries anything shaped like a credential.

Runs in the job that ran the model, before its output is uploaded as an
artifact (artifacts of a public repository can be downloaded by any signed-in
user, and log masking does not apply to them), and again where the output is
applied. On a match the file is emptied and a marker is written beside it, so
the publishing job can make the run red without ever seeing the content.

Usage:
  guard.py <result.json>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SECRET = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|sk-ant-[A-Za-z0-9_-]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
REFUSED_MARKER = "refused"


def contains_secret(text: str) -> bool:
    return bool(SECRET.search(text))


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists() or not contains_secret(path.read_text(encoding="utf-8", errors="replace")):
        return 0
    path.write_text("", encoding="utf-8")
    (path.parent / REFUSED_MARKER).write_text("model output contained a credential-shaped string\n", encoding="utf-8")
    print("::error::Model output contains something shaped like a credential; it was discarded before upload.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
