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


def parse_posts(soup: BeautifulSoup, max_posts: int) -> list[dict[str, str]]:
    """One post per row of the browse table.

    Each row (div.xtr) holds the subject twice (a <span> and the
    a.msg-detail link), then the from and date cells. Read the cells of the
    row instead of the page text, and key posts on the message URL: replies
    share a subject, so the subject cannot identify a message.
    """
    posts: list[dict[str, str]] = []
    seen: set[str] = set()

    rows = soup.select("div.xtr")
    if not rows:
        # The page changed shape; fail the track rather than publish no mail.
        raise SystemExit("mailarchive: no div.xtr rows in the browse page")

    for row in rows:
        anchor = row.find("a", class_="msg-detail", href=MESSAGE_HREF_RE)
        if anchor is None:
            continue
        subject = compact_whitespace(anchor.get_text(" ", strip=True))
        if not SUBJECT_RE.search(subject):
            continue
        url = f"https://mailarchive.ietf.org{anchor['href']}"
        if url in seen:
            continue

        sender_cell = row.select_one(".from-col")
        date_cell = row.select_one(".date-col")
        parsed = parse_date(date_cell.get_text(strip=True)) if date_cell else None

        seen.add(url)
        posts.append(
            {
                "subject": subject,
                "sender": compact_whitespace(sender_cell.get_text(" ", strip=True)) if sender_cell else "",
                "date": parsed.isoformat() if parsed else "",
                "url": url,
            }
        )
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

    posts = parse_posts(soup, int(src.get("max_posts", 120)))
    topic_counts = detect_topics(posts)
    top_senders = [
        {"sender": sender, "count": count}
        for sender, count in Counter([p["sender"] for p in posts if p["sender"]]).most_common(10)
    ]

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
