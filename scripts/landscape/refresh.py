#!/usr/bin/env python3
"""Refresh the identity-spec map's status and re-verify every sourced claim.

Inputs (curated, reviewed through pull requests):
  data/landscape.json            the specs, their layers and relations
  data/landscape-sources.json    OpenID statuses and adoption claims, each
                                 with an official URL and an exact phrase
                                 from that page as evidence

Output (written by CI, no model involved):
  data/landscape-status.json     per spec: where it stands (from the
                                 Datatracker for IETF documents, from the
                                 sourced page for OpenID ones); per claim:
                                 whether its evidence phrase is still on its
                                 page, and when that was checked

A claim whose evidence disappears is kept but marked, so the site can say
"not re-verified since" instead of silently showing stale adoption.

Evidence is one phrase or a list of phrases, all of which must be in the
page's visible text (case- and whitespace-insensitive; a phrase may also cite
a link's href). With "evidence_in_order": true they must
also appear in that order, which ties a list entry to the section around it
(for example, between a "Supported features" heading and the next one).

Usage:
  refresh.py           refresh and write data/landscape-status.json
  refresh.py --check   check only (PR check). Writes nothing unless --out is
                       given.
  Either way, the exit status is 1 if any OpenID status, external status or
  claim is not verified, or any status fell back to the previous run.
  --out PATH           write the result to PATH instead of
                       data/landscape-status.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
API = "https://datatracker.ietf.org/api/v1"
TIMEOUT = 30
SESSION = requests.Session()
SESSION.headers["User-Agent"] = "identity-deep-dive-landscape/0.1 (+https://github.com/0-draft/identity-deep-dive)"

# Datatracker state names, furthest stage wins (same mapping as the site's board).
STAGE_STATES = [
    ("rfced", {"RFC Ed Queue", "RFC-Ed-Ack", "AUTH48", "AUTH48-DONE", "EDIT", "MISSREF", "REF", "TO"}),
    (
        "iesg",
        {
            "Publication Requested",
            "Submitted to IESG for Publication",
            "AD Evaluation",
            "IESG Evaluation",
            "IESG Evaluation - Defer",
            "In Last Call",
            "Waiting for AD Go-Ahead",
            "Waiting for Writeup",
            "Approved-announcement to be sent",
            "Approved-announcement sent",
        },
    ),
    ("wglc", {"In WG Last Call", "WG Consensus: Waiting for Write-Up", "Waiting for WG Chair Go-Ahead"}),
]


def get_json(url: str) -> dict:
    for attempt in range(4):
        r = SESSION.get(url, timeout=TIMEOUT)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()
    return {}


_state_names: dict[str, str] = {}


def state_name(uri: str) -> str:
    if not _state_names:
        for o in get_json(f"{API}/doc/state/?format=json&limit=1000").get("objects", []):
            _state_names[o["resource_uri"]] = o["name"]
    return _state_names.get(uri, "")


def ietf_status(ietf: dict) -> dict:
    if "rfc" in ietf:
        n = int(ietf["rfc"])
        doc = get_json(f"{API}/doc/document/rfc{n}/?format=json")
        return {
            "stage": "rfc",
            "label": f"RFC {n}",
            "title": doc.get("title", ""),
            "url": f"https://www.rfc-editor.org/rfc/rfc{n}",
        }
    name = ietf["draft"]
    became = get_json(f"{API}/doc/relateddocument/?source__name={name}&relationship__slug=became_rfc&format=json")
    targets = [o["target"] for o in became.get("objects", [])]
    if targets:
        m = re.search(r"rfc(\d+)", targets[0])
        if m:
            return ietf_status({"rfc": int(m.group(1))}) | {"from_draft": name}
    doc = get_json(f"{API}/doc/document/{name}/?format=json")
    labels = [state_name(u) for u in doc.get("states", [])]
    labels = [l for l in labels if l]
    stage = next((s for s, names in STAGE_STATES if names & set(labels)), "wg")
    if "Expired" in labels or "Dead" in labels:
        stage = "expired"
    return {
        "stage": stage,
        "label": f"{name}-{doc.get('rev', '')}",
        "title": doc.get("title", ""),
        "states": labels,
        "updated": str(doc.get("time", ""))[:10],
        "url": f"https://datatracker.ietf.org/doc/{name}/",
    }


def page_text(url: str) -> tuple[str, str]:
    """The page's visible text, and the same text with each link's href
    written out before the link text (so a phrase can cite a link target).
    Scripts, styles, comments and other attributes are never searched."""
    r = SESSION.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    body = re.sub(r"<!--.*?-->", " ", r.text, flags=re.S)
    body = re.sub(r"<(script|style|noscript|template)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
    def strip(h: str) -> str:
        # Inline tags vanish without a gap, so "(<a>RFC 9449</a>)." reads
        # "(RFC 9449)."; every other tag separates words.
        h = re.sub(r"</?(?:a|abbr|b|cite|code|em|i|kbd|mark|q|s|small|span|strong|sub|sup|time|u|var)\b[^>]*>", "", h, flags=re.I)
        return html.unescape(re.sub(r"<[^>]+>", " ", h))

    with_hrefs = re.sub(r"""<a\b[^>]*?\bhref\s*=\s*["']([^"']*)["'][^>]*>""", r" \1 ", body, flags=re.I)
    return strip(body), strip(with_hrefs)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def phrases_found(haystack: str, phrases: list[str], in_order: bool) -> bool:
    pos = 0
    for p in map(norm, phrases):
        i = haystack.find(p, pos if in_order else 0)
        if i < 0:
            return False
        pos = i + len(p)
    return True


def evidence_found(url: str, evidence: str | list[str], in_order: bool = False) -> tuple[bool, str]:
    """Whether every evidence phrase is on the page, in order if asked.

    The visible text and the text with hrefs inlined are searched separately,
    and a match in either counts.
    """
    phrases = [evidence] if isinstance(evidence, str) else list(evidence)
    if not phrases or not all(p.strip() for p in phrases):
        return False, "empty evidence"
    try:
        text, with_hrefs = page_text(url)
    except requests.RequestException as exc:
        return False, f"fetch failed: {type(exc).__name__}"
    ok = any(phrases_found(norm(h), phrases, in_order) for h in (text, with_hrefs))
    return ok, "" if ok else "evidence not found"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only; write nothing, exit 1 on any failure")
    ap.add_argument("--out", type=Path, help="where to write the result (default: data/landscape-status.json)")
    args = ap.parse_args()

    catalogue = json.loads((DATA / "landscape.json").read_text(encoding="utf-8"))
    sources = json.loads((DATA / "landscape-sources.json").read_text(encoding="utf-8"))
    today = dt.date.today().isoformat()
    previous = {}
    prev_path = DATA / "landscape-status.json"
    if prev_path.exists():
        previous = json.loads(prev_path.read_text(encoding="utf-8"))

    statuses: dict[str, dict] = {}
    for spec in catalogue["specs"]:
        sid = spec["id"]
        try:
            if "ietf" in spec:
                statuses[sid] = ietf_status(spec["ietf"])
            elif spec.get("openid"):
                src = sources["status"].get(sid)
                if not src:
                    statuses[sid] = {"stage": "unknown", "label": ""}
                    continue
                ok, err = evidence_found(src["url"], src["evidence"], src.get("evidence_in_order", False))
                statuses[sid] = {
                    "stage": "openid-" + src["status"].lower().replace("'", "").replace(" ", "-"),
                    "label": src["status"],
                    "note": src.get("note", ""),
                    "note_ja": src.get("note_ja", ""),
                    "url": src["url"],
                    "verified": ok,
                    **({"error": err} if err else {}),
                }
            elif "external" in spec:
                ext = spec["external"]
                ok, err = evidence_found(ext["url"], ext["evidence"], ext.get("evidence_in_order", False))
                statuses[sid] = {
                    "stage": "external",
                    "label": ext.get("label", ""),
                    "url": ext["url"],
                    "verified": ok,
                    **({"error": err} if err else {}),
                }
        except Exception as exc:  # noqa: BLE001 - keep the last good status
            old = previous.get("specs", {}).get(sid)
            statuses[sid] = (old or {"stage": "unknown", "label": ""}) | {"stale": True, "error": str(exc)[:120]}
        time.sleep(0.2)

    adoption = []
    for claim in sources["adoption"]:
        try:
            ok, err = evidence_found(claim["url"], claim["evidence"], claim.get("evidence_in_order", False))
        except Exception as exc:  # noqa: BLE001 - mark the claim, keep the run going
            ok, err = False, f"check failed: {type(exc).__name__}"
        old = next(
            (a for a in previous.get("adoption", []) if a.get("url") == claim["url"] and a.get("spec") == claim["spec"]),
            {},
        )
        adoption.append(
            {
                **claim,
                "verified": ok,
                # Last date the evidence was actually seen on the page.
                "verified_on": today if ok else old.get("verified_on"),
                **({"error": err} if err else {}),
            }
        )
        time.sleep(0.2)

    bad_status = {k: v for k, v in statuses.items() if v.get("stale") or v.get("verified") is False}
    bad = [a for a in adoption if not a["verified"]]
    print(f"landscape: {len(statuses)} specs, {len(adoption)} claims, {len(bad_status)} statuses and {len(bad)} claims not verified")
    for k, v in bad_status.items():
        print(f"  status not verified: {k}: {v.get('url', '')} {v.get('error', '')}")
    for a in bad:
        print(f"  claim not verified: {a['spec']} / {a['who']}: {a['url']} {a.get('error', '')}")
    out = {"generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(), "specs": statuses, "adoption": adoption}
    if args.out or not args.check:
        (args.out or prev_path).write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 1 if (bad or bad_status) else 0

if __name__ == "__main__":
    sys.exit(main())
