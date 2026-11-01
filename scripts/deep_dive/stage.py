#!/usr/bin/env python3
"""Pick the next deep-dive subject for a track and stage its source material.

The subject is the highest candidate in candidates.json (which already
carries Claude's triage order) that has no deep-dive directory yet and no
open deep-dive branch. Source material is fetched here, as plain files, so the
Claude pass that writes the deep dive only needs read tools.

Usage:
  stage.py --track oauth-wg --out deep-dive-work [--candidate draft-ietf-oauth-sd-jwt-vc]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "insights"))
from changes import (  # noqa: E402
    REPO_ROOT,
    TRACKS,
    UNTRUSTED_HEADER,
    cap,
    candidate_key,
    draft_material,
    draft_txt,
    get,
    mail_material,
)
from write import is_safe_slug  # noqa: E402

DRAFT_RE = re.compile(r"\b(draft-[a-z0-9-]+?)-(\d{2})\b")
SOURCE_CAP = 250_000
DIFF_CAP = 80_000
MAILS = 6
README_CAP = 40_000


def subject_for(track: str, cand: dict, state: dict) -> dict[str, Any] | None:
    key = candidate_key(track, cand)
    if track == "openid":
        if not key.startswith("openid/"):
            return None
        return {"kind": "repo", "name": key, "slug": key.split("/", 1)[1], "url": cand.get("html_url", "")}
    if track == "oauth-wg":
        name = cand.get("draft_name")
        if not name:
            return None
        rev = next((str(d.get("rev")) for d in state.get("drafts", []) if d.get("name") == name), "")
    else:
        m = DRAFT_RE.search(key)
        if not m:
            return None
        name, rev = m.group(1), m.group(2)
    if not rev:
        return None
    all_drafts = state.get("drafts", []) + state.get("active_drafts", []) + state.get("related_drafts", [])
    labels = next((d.get("state_labels") for d in all_drafts if d.get("name") == name), None)
    return {
        "datatracker_states": labels or [],
        "kind": "draft",
        "name": name,
        "rev": rev,
        "slug": name,
        "url": f"https://datatracker.ietf.org/doc/{name}/{rev}/",
    }


def already_proposed(branch: str) -> bool:
    """A branch is still open, or a PR from it was closed (merged or rejected).

    A merged deep dive also has its directory on main; a rejected one does
    not, and without this check it would be drafted again every week.
    """
    res = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    if res.returncode == 0:
        return True
    if res.returncode != 2:
        # 2 is "no such ref"; anything else (network, auth) is unknown, and
        # like the gh check below, unknown means skip.
        print(f"stage: could not check origin for {branch}: {res.stderr.decode(errors='replace').strip()}", file=sys.stderr)
        return True
    res = subprocess.run(
        ["gh", "pr", "list", "--state", "closed", "--head", branch, "--json", "number", "--jq", "length"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        # Cannot tell: better to skip a subject than to re-propose a rejected one.
        print(f"stage: could not list closed PRs for {branch}: {res.stderr.strip()}", file=sys.stderr)
        return True
    return res.stdout.strip() not in ("", "0")


def stage_draft(subject: dict, state: dict, out: Path) -> list[str]:
    name, rev = subject["name"], subject["rev"]
    files = []
    try:
        text = draft_txt(name, rev)
    except Exception as exc:  # noqa: BLE001 - any failure means no deep dive
        raise SystemExit(f"stage: could not fetch {name}-{rev}: {exc}")
    (out / "source.txt").write_text(
        UNTRUSTED_HEADER + f"Full text of {name}-{rev}\n{subject['url']}\n-----\n\n" + cap(text, SOURCE_CAP),
        encoding="utf-8",
    )
    files.append("source.txt")
    if int(rev) > 0:
        prev = f"{int(rev) - 1:02d}"
        (out / "diff.txt").write_text(UNTRUSTED_HEADER + draft_material(name, rev, prev, diff_cap=DIFF_CAP), encoding="utf-8")
        files.append("diff.txt")

    # The exact draft, with or without a revision: draft-x and draft-x-22,
    # never draft-x-extra.
    mentions = re.compile(rf"(?<![\w-]){re.escape(name)}(?:-\d{{2}})?(?![\w-])")
    mails = [
        m
        for m in state.get("mail_posts", []) + state.get("mail_messages", [])
        if mentions.search(m.get("subject") or "") and (m.get("url") or "").startswith("https://mailarchive.ietf.org/")
    ]
    if mails:
        parts = [f"Message: {m.get('subject', '')}\n{m['url']}\n\n{mail_material(m['url'])}" for m in mails[:MAILS]]
        rest = [f"- {m.get('subject', '')} {m['url']}" for m in mails[MAILS:]]
        (out / "mail.txt").write_text(
            UNTRUSTED_HEADER
            + "Mailing-list messages that mention the draft:\n\n"
            + "\n\n=====\n\n".join(parts)
            + ("\n\nMore messages, subjects only:\n" + "\n".join(rest) if rest else "")
            + "\n",
            encoding="utf-8",
        )
        files.append("mail.txt")
    return files


def stage_repo(subject: dict, state: dict, out: Path) -> list[str]:
    repo = subject["name"]
    try:
        readme = get(f"https://api.github.com/repos/{repo}/readme", github=True)
        readme_text = get(readme.json()["download_url"]).text
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"stage: could not fetch README of {repo}: {exc}")
    pulls = get(f"https://api.github.com/repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page=30", github=True).json()
    lines = [f"- #{p['number']} [{p['state']}{', merged' if p.get('merged_at') else ''}] {p['title']}" for p in pulls]
    (out / "source.txt").write_text(
        UNTRUSTED_HEADER
        + f"Repository {repo}\n{subject['url']}\n-----\n\nREADME:\n\n{cap(readme_text, README_CAP)}\n\n"
        + "Recently updated pull requests:\n"
        + "\n".join(lines)
        + "\n",
        encoding="utf-8",
    )
    return ["source.txt"]


def insights_for(track_dir: Path, name: str) -> str:
    path = track_dir / "data" / "normalized" / "insights.json"
    if not path.exists():
        return ""
    items = json.loads(path.read_text(encoding="utf-8")).get("items", {}).values()
    # Exact subject only: draft-x must not pick up draft-x-vc, nor
    # openid/authzen pick up openid/authzen-foo.
    draft_id = re.compile(rf"^draft:{re.escape(name)}-\d{{2}}$")
    hits = [i for i in items if draft_id.match(i.get("id", "")) or i.get("id", "").startswith(f"repo:{name}:")]
    return "\n\n".join(f"## {i['title']}\n\n{i['headline']}\n\n{i['summary']}" for i in hits)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=TRACKS, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--candidate", default="", help="Candidate key to use instead of the top one")
    args = ap.parse_args()

    track_dir = REPO_ROOT / "tracks" / args.track
    norm = track_dir / "data" / "normalized"
    state = json.loads((norm / "state.json").read_text(encoding="utf-8"))
    cands = json.loads((norm / "candidates.json").read_text(encoding="utf-8")).get("candidates", [])
    if args.candidate:
        cands = [c for c in cands if candidate_key(args.track, c) == args.candidate]
        if not cands:
            # With track "all" the other tracks' legs land here; not an error.
            print(f"::notice::stage: {args.candidate!r} is not a candidate in {args.track}; nothing to draft here")

    subject = None
    for cand in cands:
        s = subject_for(args.track, cand, state)
        if not s or not is_safe_slug(s["slug"]):
            continue
        s["branch"] = f"deep-dive/{args.track}/{s['slug']}"
        if (track_dir / "deep-dives" / s["slug"]).exists() or already_proposed(s["branch"]):
            continue
        s["candidate"] = candidate_key(args.track, cand)
        s["ai_note"] = cand.get("ai_note", "")
        subject = s
        break

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if subject is None:
        print("stage: no candidate without a deep dive")
        # A marker the publishing job can tell apart from a missing artifact.
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "none").write_text("no candidate without a deep dive\n", encoding="utf-8")
        if gh_out:
            with open(gh_out, "a", encoding="utf-8") as fh:
                fh.write("found=false\n")
        return 0

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    files = stage_draft(subject, state, out) if subject["kind"] == "draft" else stage_repo(subject, state, out)
    notes = insights_for(track_dir, subject["name"])
    if notes:
        (out / "insights.md").write_text(
            "# Earlier briefings on this subject (written by this repository's insight pass)\n\n" + notes + "\n",
            encoding="utf-8",
        )
        files.append("insights.md")
    subject["files"] = files
    subject["track"] = args.track
    (out / "subject.json").write_text(json.dumps(subject, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write(f"found=true\nslug={subject['slug']}\nbranch={subject['branch']}\n")
    print(f"stage: {subject['name']} -> {subject['branch']} ({', '.join(files)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
