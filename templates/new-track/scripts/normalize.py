#!/usr/bin/env python3
"""Merge raw collector outputs into a single normalized state.json."""
from __future__ import annotations

from _common import ROOT, iso_now, raw_output_path, read_json, write_json


def main() -> None:
    state = {"generated_at": iso_now(), "sources": {}}

    github_path = raw_output_path("github")
    if github_path.exists():
        gh = read_json(github_path)
        state["sources"]["github"] = gh.get("collected_at", "")
        state["github_repos"] = gh.get("repos", [])

    write_json(ROOT / "data" / "normalized" / "state.json", state)
    print(f"normalize: sources={list(state['sources'].keys())}")


if __name__ == "__main__":
    main()
