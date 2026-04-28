from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
DEFAULT_HEADERS = {
    "User-Agent": "deep-dive/0.1",
    "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
LINK_RE = re.compile(r'<([^>]+)>;\s*rel="([^"]+)"')


def now_utc() -> dt.datetime:
    return dt.datetime.now(tz=UTC)


def iso_now() -> str:
    return now_utc().replace(microsecond=0).isoformat()


def today_utc() -> dt.date:
    return now_utc().date()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def load_sources(path: Path) -> dict[str, Any]:
    """Load sources.yaml and normalize github.repos entries to dict form.

    Each repo may be either a bare string ``"org/name"`` or a mapping with
    ``{repo, weight, category, note}``. The returned shape always uses the
    mapping form with defaults filled in (``weight=1.0``, ``category=None``,
    ``note=None``), so downstream code can treat all tracks uniformly.
    """
    data = load_yaml(path) or {}
    github = data.get("github") or {}
    repos = github.get("repos") or []
    normalized: list[dict[str, Any]] = []
    for entry in repos:
        if isinstance(entry, str):
            normalized.append({"repo": entry, "weight": 1.0, "category": None, "note": None})
        elif isinstance(entry, dict):
            normalized.append(
                {
                    "repo": entry.get("repo") or entry.get("name") or "",
                    "weight": float(entry.get("weight", 1.0)),
                    "category": entry.get("category"),
                    "note": entry.get("note"),
                }
            )
    if "github" in data:
        data["github"] = {**github, "repos": normalized}
    return data


def env_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _build_headers(url: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = dict(DEFAULT_HEADERS)
    host = urlparse(url).hostname or ""
    if host.endswith("api.github.com"):
        token = env_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        headers.setdefault("Accept", "application/vnd.github+json")
        headers.setdefault("X-GitHub-Api-Version", "2022-11-28")
    if extra:
        headers.update(extra)
    return headers


def _request(url: str, *, timeout: int, extra_headers: dict[str, str] | None = None) -> requests.Response:
    """GET with 429/5xx-aware retry. Honors Retry-After when present."""
    backoff = 1.0
    for attempt in range(5):
        resp = requests.get(url, headers=_build_headers(url, extra_headers), timeout=timeout)
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            retry_after = resp.headers.get("Retry-After")
            sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else backoff
            time.sleep(min(sleep_s, 30.0))
            backoff = min(backoff * 2, 30.0)
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


def fetch_text(url: str, timeout: int = 30) -> str:
    resp = _request(url, timeout=timeout)
    resp.encoding = resp.encoding or "utf-8"
    return resp.text


def fetch_json(url: str, timeout: int = 30) -> Any:
    resp = _request(url, timeout=timeout)
    return resp.json()


def github_paginate(
    url: str,
    *,
    per_page: int = 100,
    max_pages: int = 50,
    timeout: int = 30,
) -> Iterator[Any]:
    """Yield items from a GitHub REST endpoint, walking ``Link: rel="next"``.

    Works for both list endpoints (``/orgs/x/repos``) and search endpoints
    (``/search/issues``); for the latter the per-page payload is an object
    with an ``items`` array, which the caller can flatten.
    """
    sep = "&" if "?" in url else "?"
    next_url: str | None = f"{url}{sep}per_page={per_page}"
    pages = 0
    while next_url and pages < max_pages:
        resp = _request(next_url, timeout=timeout)
        yield resp.json()
        pages += 1
        link = resp.headers.get("Link", "")
        next_url = None
        for match in LINK_RE.finditer(link):
            href, rel = match.group(1), match.group(2)
            if rel == "next":
                next_url = href
                break


def raw_output_path(source: str, date_value: dt.date | None = None) -> Path:
    d = date_value or today_utc()
    return ROOT / "data" / "raw" / f"{d:%Y-%m-%d}" / f"{source}.json"


def parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None

    if DATE_RE.fullmatch(value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None

    match = DATE_RE.search(value)
    if not match:
        return None

    try:
        return dt.date.fromisoformat(match.group(0))
    except ValueError:
        return None


def compact_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_iso8601(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return dt.datetime.fromisoformat(s)
    except ValueError:
        return None


def days_since(value: str | None, *, reference: dt.datetime | None = None) -> int | None:
    parsed = parse_iso8601(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    ref = reference or now_utc()
    return (ref - parsed).days
