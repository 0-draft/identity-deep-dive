from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
DEFAULT_HEADERS = {
    "User-Agent": "deep-dive-track/0.1",
    "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
}


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
        return yaml.safe_load(fh) or {}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def fetch_json(url: str, timeout: int = 30) -> Any:
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def raw_output_path(source: str, date_value: dt.date | None = None) -> Path:
    d = date_value or today_utc()
    return ROOT / "data" / "raw" / d.isoformat() / f"{source}.json"
