from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from _common import (
    ROOT,
    compact_whitespace,
    fetch_text,
    iso_now,
    load_yaml,
    parse_date,
    raw_output_path,
    write_json,
)

DRAFT_LINE_RE = re.compile(r"^draft-[a-z0-9-]+-\d{2}$")
SESSION_RE = re.compile(r"^(IETF \d+|interim-\d{4}-wimse-\d+)$", re.IGNORECASE)


def clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = compact_whitespace(raw)
        if line:
            lines.append(line)
    return lines


def split_name_rev(name_rev: str) -> tuple[str, str]:
    idx = name_rev.rfind("-")
    if idx < 0:
        return name_rev, ""
    return name_rev[:idx], name_rev[idx + 1 :]


def find_section_bounds(lines: list[str], start_marker: str, end_marker: str | None) -> tuple[int, int]:
    start = -1
    for i, line in enumerate(lines):
        if start_marker in line:
            start = i + 1
            break
    if start < 0:
        return -1, -1

    end = len(lines)
    if end_marker:
        for i in range(start, len(lines)):
            if end_marker in lines[i]:
                end = i
                break
    return start, end


def parse_drafts(lines: list[str], start_marker: str, end_marker: str | None) -> list[dict[str, Any]]:
    start, end = find_section_bounds(lines, start_marker, end_marker)
    if start < 0:
        return []

    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    i = start
    while i < end:
        line = lines[i]
        if DRAFT_LINE_RE.match(line):
            name, revision = split_name_rev(line)
            title = ""
            date = ""

            for j in range(i + 1, min(i + 8, end)):
                candidate = lines[j]
                if not title and not DRAFT_LINE_RE.match(candidate):
                    title = candidate
                parsed_date = parse_date(candidate)
                if parsed_date:
                    date = parsed_date.isoformat()
                    break

            if line not in seen:
                results.append(
                    {
                        "name_rev": line,
                        "name": name,
                        "revision": revision,
                        "title": title,
                        "date": date,
                    }
                )
                seen.add(line)
        i += 1

    return results


def parse_meetings(lines: list[str]) -> list[dict[str, str]]:
    meetings: list[dict[str, str]] = []
    seen: set[str] = set()

    for i, line in enumerate(lines):
        if not SESSION_RE.match(line):
            continue

        date = ""
        for j in range(i, min(i + 15, len(lines))):
            parsed_date = parse_date(lines[j])
            if parsed_date:
                date = parsed_date.isoformat()
                break

        if line not in seen:
            meetings.append({"session": line, "date": date})
            seen.add(line)

    return meetings


def parse_history(lines: list[str]) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    for line in lines:
        if "Area Director changed" not in line:
            continue
        parsed_date = parse_date(line)
        if not parsed_date:
            continue
        events.append({"date": parsed_date.isoformat(), "event": line})
    return events


def as_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n")


def main() -> None:
    cfg = load_yaml(ROOT / "config" / "sources.yaml")
    src = cfg["datatracker"]

    documents_html = fetch_text(src["documents_url"])
    meetings_html = fetch_text(src["meetings_url"])
    history_html = fetch_text(src["history_url"])

    document_lines = clean_lines(as_text(documents_html))
    meetings_lines = clean_lines(as_text(meetings_html))
    history_lines = clean_lines(as_text(history_html))

    active_drafts = parse_drafts(document_lines, "Active Internet-Drafts", "Related Internet-Drafts and RFCs")
    related_drafts = parse_drafts(document_lines, "Related Internet-Drafts and RFCs", "Atom feed")
    meetings = parse_meetings(meetings_lines)
    ad_history = parse_history(history_lines)

    normalized = {
        "collected_at": iso_now(),
        "source": "datatracker",
        "source_urls": src,
        "active_drafts": active_drafts,
        "related_drafts": related_drafts,
        "meetings": meetings,
        "ad_history": ad_history,
        "stats": {
            "active_drafts": len(active_drafts),
            "related_drafts": len(related_drafts),
            "meetings": len(meetings),
            "ad_history_events": len(ad_history),
        },
    }

    raw = {
        "collected_at": normalized["collected_at"],
        "source": "datatracker",
        "source_urls": src,
        "documents_html": documents_html,
        "meetings_html": meetings_html,
        "history_html": history_html,
    }

    write_json(raw_output_path("datatracker"), raw)
    write_json(ROOT / "data" / "normalized" / "datatracker.json", normalized)
    print(f"datatracker: active={len(active_drafts)} related={len(related_drafts)} meetings={len(meetings)}")


if __name__ == "__main__":
    main()
