from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
DEFAULT_HEADERS = {
    "User-Agent": "ietf-wimse-deep-dive/0.1",
    "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


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


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def fetch_text(url: str, timeout: int = 30) -> str:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.encoding or "utf-8"
    return resp.text


def fetch_json(url: str, timeout: int = 30) -> Any:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


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
