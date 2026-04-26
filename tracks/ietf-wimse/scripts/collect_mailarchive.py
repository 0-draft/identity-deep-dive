from __future__ import annotations

import re
from collections import Counter
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

SUBJECT_RE = re.compile(r"\[WIMSE\]", re.IGNORECASE)
MESSAGE_HREF_RE = re.compile(r"^/arch/msg/wimse/")

TOPIC_PATTERNS: dict[str, list[str]] = {
    "ai-agent": [r"\bai\b", r"agent"],
    "attestation": [r"attestation", r"evidence", r"rats"],
    "credential-brokering": [r"credential", r"broker"],
    "wpt": [r"wpt", r"proof token"],
    "http-signature": [r"http signature", r"signature"],
    "mutual-tls": [r"mutual tls", r"mTLS", r"mtls"],
    "meeting-minutes": [r"minutes", r"ietf \d+"],
    "github-digest": [r"weekly github digest", r"repository activity summary"],
}


def clean_lines(text: str) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        line = compact_whitespace(raw)
        if line:
            out.append(line)
    return out


def map_subject_to_link(soup: BeautifulSoup) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for anchor in soup.find_all("a", href=MESSAGE_HREF_RE):
        subject = compact_whitespace(anchor.get_text(" ", strip=True))
        href = anchor.get("href", "")
        if subject and href and subject not in mapping:
            mapping[subject] = f"https://mailarchive.ietf.org{href}"
    return mapping


def parse_posts(lines: list[str], max_posts: int) -> list[dict[str, str]]:
    posts: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for i, line in enumerate(lines):
        if not SUBJECT_RE.search(line):
            continue

        subject = line
        sender = ""
        date = ""

        for j in range(i + 1, min(i + 8, len(lines))):
            candidate = lines[j]
            if not sender and candidate.lower() not in {"wimse", "subject", "from", "date", "list"}:
                if not parse_date(candidate):
                    sender = candidate
            parsed = parse_date(candidate)
            if parsed:
                date = parsed.isoformat()
                break

        key = (subject, sender, date)
        if key in seen:
            continue

        seen.add(key)
        posts.append({"subject": subject, "sender": sender, "date": date})
        if len(posts) >= max_posts:
            break

    return posts


def detect_topics(posts: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()

    for post in posts:
        haystack = post["subject"].lower()
        for topic, patterns in TOPIC_PATTERNS.items():
            if all(re.search(pattern, haystack, flags=re.IGNORECASE) for pattern in patterns):
                counts[topic] += 1

    return [
        {"topic": topic, "count": count}
        for topic, count in counts.most_common()
    ]


def main() -> None:
    cfg = load_yaml(ROOT / "config" / "sources.yaml")
    src = cfg["mailarchive"]

    html = fetch_text(src["browse_url"])
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n")
    lines = clean_lines(text)

    posts = parse_posts(lines, int(src.get("max_posts", 120)))
    topic_counts = detect_topics(posts)
    top_senders = [
        {"sender": sender, "count": count}
        for sender, count in Counter([p["sender"] for p in posts if p["sender"]]).most_common(10)
    ]

    subject_link = map_subject_to_link(soup)
    for post in posts:
        post["url"] = subject_link.get(post["subject"], "")

    normalized = {
        "collected_at": iso_now(),
        "source": "mailarchive",
        "source_url": src["browse_url"],
        "posts": posts,
        "topic_counts": topic_counts,
        "top_senders": top_senders,
        "stats": {
            "posts": len(posts),
            "topics": len(topic_counts),
        },
    }

    raw = {
        "collected_at": normalized["collected_at"],
        "source": "mailarchive",
        "source_url": src["browse_url"],
        "html": html,
    }

    write_json(raw_output_path("mailarchive"), raw)
    write_json(ROOT / "data" / "normalized" / "mailarchive.json", normalized)
    print(f"mailarchive: posts={len(posts)} topics={len(topic_counts)}")


if __name__ == "__main__":
    main()
