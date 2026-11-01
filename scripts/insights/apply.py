#!/usr/bin/env python3
"""Validate Claude's structured insight output and fold it into a track.

- Merges new insights into tracks/<track>/data/normalized/insights.json, a
  rolling window of the last RETENTION_DAYS days.
- Annotates candidates.json with Claude's triage (ai_priority / ai_note) and
  reorders it: high first, then unrated/normal, then low, keeping the
  heuristic order within each tier.
- Writes a "Briefing" section into the latest daily report.

Claude's output is treated as untrusted: ids and candidate keys must match
what changes.py staged, cross-track links must name something that exists,
text is HTML-escaped, and diagrams are restricted to plain mermaid. URLs are
never taken from Claude; every link comes from changes.json.

Run without --result to re-render from the stored window only (report.py
rewrites the daily report on every run, so this has to happen every time).
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from changes import TRACKS, baseline_path, candidate_key, track_index  # noqa: E402

RETENTION_DAYS = 7
REPORT_DAYS = 3
REPORT_MAX_ITEMS = 12
SIGNIFICANCE = {"substantive", "editorial", "new-proposal", "discussion", "routine"}
PRIORITIES = {"high": 0, "normal": 1, "low": 2}
MERMAID_START = re.compile(r"^(flowchart|graph|sequenceDiagram)\b")
MERMAID_FORBIDDEN = ("```", "%%{", "click ", "javascript:", "href", "callback", "insights:")
# Anything that reads as an HTML tag or comment. Mermaid arrows (-->, ->>,
# <-->) never put a letter, "/", "!" or "?" right after "<".
HTML_LIKE = re.compile(r"<[A-Za-z/!?]")
# Credentials an injected source might talk the model into echoing back.
SECRET = re.compile(r"(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9_-]{20,})")
SECTION_START = "<!-- insights:start -->"
SECTION_END = "<!-- insights:end -->"


def text(value: Any, limit: int, *, oneline: bool = False) -> str:
    s = str(value or "").strip()
    s = re.sub(r"\s+", " ", s) if oneline else re.sub(r"[ \t]+\n", "\n", s)
    s = html.escape(s[:limit], quote=False)
    # Markdown link and image syntax survives HTML escaping, and the site
    # renders this with marked, so `[x](javascript:...)` would become a link.
    return s.replace("[", "\\[").replace("]", "\\]")


def mermaid(src: Any) -> str:
    s = str(src or "").strip()
    if not s or len(s) > 2500 or len(s.splitlines()) > 40:
        return ""
    if not MERMAID_START.match(s):
        return ""
    lowered = s.lower()
    if any(bad in lowered for bad in MERMAID_FORBIDDEN) or HTML_LIKE.search(s):
        return ""
    # Mermaid ends a statement at ";" and reads "#" as the start of an entity
    # code, so either one inside a label breaks the whole diagram.
    return s.replace(";", ",").replace("#", "no. ")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def known_names() -> dict[str, set[str]]:
    return {t: {line.split(":", 1)[0].strip() for line in track_index(t)} for t in TRACKS}


def merge(store: dict, result: dict, changes: dict, track: str, today: str, now: str) -> list[str]:
    """Merge validated output into store. Returns warnings."""
    warnings: list[str] = []
    staged = {i["id"]: i for i in changes.get("items", [])}
    keys = set(changes.get("candidate_keys", []))
    names = known_names()

    brief = text(result.get("brief"), 400, oneline=True)
    if brief:
        store.setdefault("briefs", []).append({"at": now, "text": brief})

    for raw in result.get("items", []):
        iid = raw.get("id")
        if iid not in staged:
            warnings.append(f"dropped item with unknown id: {str(iid)[:80]}")
            continue
        sig = raw.get("significance")
        related = []
        for r in raw.get("related", []) or []:
            rt, rn = r.get("track"), str(r.get("name", "")).strip()
            if rt in names and rt != track and rn in names[rt]:
                related.append({"track": rt, "name": rn, "note": text(r.get("note"), 240, oneline=True)})
            else:
                warnings.append(f"dropped related link {rt}/{rn[:60]} on {iid}")
        diagram = mermaid(raw.get("diagram"))
        if raw.get("diagram") and not diagram:
            warnings.append(f"dropped diagram on {iid}")
        src = staged[iid]
        store.setdefault("items", {})[iid] = {
            "id": iid,
            "kind": src["kind"],
            "title": src["title"],
            "url": src["url"],
            "first_seen": store.get("items", {}).get(iid, {}).get("first_seen", today),
            "updated_at": now,
            "headline": text(raw.get("headline"), 160, oneline=True),
            "summary": text(raw.get("summary"), 1200),
            "significance": sig if sig in SIGNIFICANCE else "routine",
            "use_cases": [text(u, 300, oneline=True) for u in (raw.get("use_cases") or [])[:3] if str(u).strip()],
            "diagram": diagram,
            "related": related,
        }

    for t in result.get("triage", []):
        key, pri = t.get("candidate"), t.get("priority")
        if key not in keys or pri not in PRIORITIES:
            warnings.append(f"dropped triage for {str(key)[:80]}")
            continue
        store.setdefault("triage", {})[key] = {
            "priority": pri,
            "reason": text(t.get("reason"), 300, oneline=True),
            "date": today,
        }
    return warnings


def prune(store: dict, today: dt.date) -> None:
    cutoff = (today - dt.timedelta(days=RETENTION_DAYS)).isoformat()
    store["items"] = {k: v for k, v in store.get("items", {}).items() if v.get("first_seen", "") >= cutoff}
    store["triage"] = {k: v for k, v in store.get("triage", {}).items() if v.get("date", "") >= cutoff}
    store["briefs"] = [b for b in store.get("briefs", []) if b.get("at", "")[:10] >= cutoff][-20:]


def annotate_candidates(track: str, store: dict, path: Path) -> None:
    if not path.exists():
        return
    data = load_json(path, {})
    cands = data.get("candidates", [])
    triage = store.get("triage", {})
    for c in cands:
        c.pop("ai_priority", None)
        c.pop("ai_note", None)
        t = triage.get(candidate_key(track, c))
        if t:
            c["ai_priority"] = t["priority"]
            c["ai_note"] = t["reason"]
    order = {id(c): i for i, c in enumerate(cands)}
    cands.sort(key=lambda c: (PRIORITIES.get(c.get("ai_priority", "normal"), 1), order[id(c)]))
    for i, c in enumerate(cands, start=1):
        if "rank" in c:
            c["rank"] = i
    data["candidates"] = cands
    dump_json(path, data)


def render(track: str, store: dict, today: dt.date) -> str:
    cutoff = (today - dt.timedelta(days=REPORT_DAYS - 1)).isoformat()
    items = [i for i in store.get("items", {}).values() if i.get("first_seen", "") >= cutoff]
    rank = {"substantive": 0, "new-proposal": 1, "discussion": 2, "editorial": 3, "routine": 4}
    items.sort(key=lambda i: (-int(i["first_seen"].replace("-", "")), rank.get(i["significance"], 9), i["id"]))
    items = items[:REPORT_MAX_ITEMS]

    lines = [SECTION_START, "## Briefing", ""]
    briefs = store.get("briefs", [])
    if briefs:
        lines += [f"> {briefs[-1]['text']}", "", f"_Updated {briefs[-1]['at']}. Machine-drafted from the sources linked below, which stay authoritative._", ""]
    if not items:
        lines += ["- Nothing new in the last few days that needed explaining.", ""]
    for i in items:
        heading = (i["headline"] or text(i["title"], 300, oneline=True)).rstrip(".:;!?")
        lines += [f"### {heading}", ""]
        lines += [f"`{i['kind']}` · `{i['significance']}` · first seen {i['first_seen']} · [{text(i['title'], 300, oneline=True)}]({i['url']})", ""]
        if i["summary"]:
            lines += [i["summary"], ""]
        if i["diagram"]:
            lines += ["```mermaid", i["diagram"], "```", ""]
        if i["use_cases"]:
            lines += ["**Use cases**", ""] + [f"- {u}" for u in i["use_cases"]] + [""]
        if i["related"]:
            lines += ["**Related in other tracks**", ""]
            lines += [f"- `{r['track']}` / `{r['name']}`: {r['note']}" for r in i["related"]] + [""]

    overflow = store.get("overflow", [])
    if overflow:
        lines += ["### Also changed, not explained", ""]
        lines += [f"- [{text(o['title'], 300, oneline=True)}]({o['url']})" for o in overflow] + [""]

    triage = store.get("triage", {})
    flagged = sorted(((k, v) for k, v in triage.items() if v["priority"] != "normal"), key=lambda kv: (PRIORITIES[kv[1]["priority"]], kv[0]))
    if flagged:
        lines += ["### Triage of the candidate queue", ""]
        lines += [f"- **{v['priority']}** `{text(k, 200, oneline=True)}`: {v['reason']}" for k, v in flagged] + [""]
    lines.append(SECTION_END)
    return "\n".join(lines) + "\n"


def write_section(report: Path, section: str) -> None:
    body = report.read_text(encoding="utf-8")
    # Greedy to the last end marker, so a marker smuggled into the section
    # cannot leave a tail of it behind.
    body = re.sub(re.escape(SECTION_START) + r".*" + re.escape(SECTION_END) + r"\n{0,2}", "", body, flags=re.S)
    # After the title and the metadata lines, before the first section.
    idx = body.find("\n## ")
    if idx == -1:
        body = body.rstrip("\n") + "\n\n" + section
    else:
        body = body[: idx + 1] + section + "\n" + body[idx + 1 :]
    report.write_text(body, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=TRACKS, required=True)
    ap.add_argument("--changes", type=Path, help="changes.json written by changes.py")
    ap.add_argument("--result", type=Path, help="Claude structured output (JSON file)")
    args = ap.parse_args()

    track_dir = REPO_ROOT / "tracks" / args.track
    norm = track_dir / "data" / "normalized"
    store_path = norm / "insights.json"
    store = load_json(store_path, {"items": {}, "triage": {}, "briefs": []})
    now_dt = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    today = now_dt.date()

    changes = load_json(args.changes, None) if args.changes else None
    merged, refused = False, False
    result: dict = {}
    raw = args.result.read_text(encoding="utf-8").strip() if args.result and args.result.exists() else ""
    if raw and SECRET.search(raw):
        # Fail closed: publish nothing from this run, and make the run red.
        print("::error::insights: Claude output contains something shaped like a credential; discarding it")
        refused = True
    elif raw and changes is not None:
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"::warning::insights: Claude output is not JSON ({exc}); keeping previous insights")
            result = None
        if isinstance(result, dict):
            for w in merge(store, result, changes, args.track, today.isoformat(), now_dt.isoformat()):
                print(f"::warning::insights: {w}")
            merged = True

    # Move the baseline only past changes that were explained, or when there
    # were none. A failed or skipped Claude pass leaves it, so the next run
    # picks the same changes up again.
    state_path = norm / "state.json"
    base = baseline_path(args.track)
    nothing_new = changes is not None and not changes.get("items")
    if state_path.exists() and (merged or nothing_new or not base.exists()):
        shutil.copyfile(state_path, base)
        if merged or nothing_new:
            # The baseline moves past these too, so list them rather than lose
            # them: items over the per-run cap, and staged items the model
            # returned nothing for.
            explained = {i.get("id") for i in result.get("items", [])} if merged else set()
            missed = [i for i in (changes or {}).get("items", []) if i.get("id") not in explained] if merged else []
            store["overflow"] = [
                {"title": o.get("title", ""), "url": o.get("url", "")}
                for o in (missed + (changes or {}).get("skipped", []))[:20]
            ]

    prune(store, today)
    dump_json(store_path, store)
    annotate_candidates(args.track, store, norm / "candidates.json")

    dailies = sorted((track_dir / "reports" / "daily").glob("*.md"))
    if dailies:
        write_section(dailies[-1], render(args.track, store, today))
    print(f"insights: {len(store['items'])} item(s) in window, {len(store['triage'])} triage note(s)")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
