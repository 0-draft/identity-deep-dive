from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

GITHUB_API_BASE = "https://api.github.com"


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def utc_today() -> date:
    return datetime.now(UTC).date()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def github_get(path: str, token: str | None = None, params: dict[str, Any] | None = None) -> Any:
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    url = f"{GITHUB_API_BASE}{path}{query}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "openid-deep-dive-radar",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url=url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def github_paginate(
    path: str,
    token: str | None = None,
    params: dict[str, Any] | None = None,
    list_key: str | None = None,
    max_pages: int = 20,
) -> list[Any]:
    out: list[Any] = []
    base = dict(params or {})
    base.setdefault("per_page", 100)

    for page in range(1, max_pages + 1):
        q = dict(base)
        q["page"] = page
        payload = github_get(path=path, token=token, params=q)

        if list_key is None:
            items = payload
        else:
            items = payload.get(list_key, [])

        if not items:
            break

        out.extend(items)

        if len(items) < int(base["per_page"]):
            break

    return out


def parse_iso8601(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def days_since(ts: str | None, now: datetime | None = None) -> int:
    if not ts:
        return 99999
    dt = parse_iso8601(ts)
    if dt is None:
        return 99999
    now_dt = now or datetime.now(UTC)
    return max(0, int((now_dt - dt).total_seconds() // 86400))


def env_token() -> str | None:
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
