from __future__ import annotations

import csv
import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator, TextIO


ROOT = Path(__file__).resolve().parents[1]


HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; brazilian-power-system-dashboard/1.0)",
    "Accept": "application/json,text/csv,*/*",
}


def read_config(path: Path | None = None) -> dict[str, Any]:
    path = path or ROOT / "config" / "config.yaml"
    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, data)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value.strip() == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(value.strip())
    return data


def parse_scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value


def ensure_dirs(config: dict[str, Any]) -> None:
    for item in config["paths"].values():
        (ROOT / item).mkdir(parents=True, exist_ok=True)


def http_json(url: str, timeout: int, retries: int) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HTTP_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Could not fetch {url}: {last_error}")


def ckan_package(api_base: str, package_id: str, timeout: int = 60, retries: int = 3) -> dict[str, Any]:
    query = urllib.parse.urlencode({"id": package_id})
    data = http_json(f"{api_base}/package_show?{query}", timeout, retries)
    if not data.get("success"):
        raise RuntimeError(f"CKAN package_show failed for {package_id}")
    return data["result"]


def find_resource(package: dict[str, Any], contains: str | None = None, prefix: str | None = None, year: int | None = None) -> dict[str, Any]:
    resources = package.get("resources", [])
    candidates = []
    for resource in resources:
        name = (resource.get("name") or "").lower()
        fmt = (resource.get("format") or "").lower()
        if fmt and fmt not in {"csv", "parquet", "zip"}:
            continue
        if contains and contains.lower() not in name:
            continue
        if prefix and not name.startswith(prefix.lower()):
            continue
        if year and str(year) not in name:
            continue
        if "csv" in fmt or "parquet" in fmt or "zip" in fmt or name.endswith(".csv") or "csv" in name:
            candidates.append(resource)
    if not candidates:
        raise RuntimeError(f"No resource found: contains={contains}, prefix={prefix}, year={year}")
    candidates.sort(key=lambda r: (r.get("name") or ""), reverse=True)
    return candidates[0]


def download(url: str, destination: Path, timeout: int, retries: int, force: bool = False) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return file_metadata(destination, url, cached=True)
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HTTP_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                with destination.open("wb") as handle:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
            if destination.stat().st_size == 0:
                raise RuntimeError(f"Empty download: {destination}")
            return file_metadata(destination, url, cached=False)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Could not download {url}: {last_error}")


def file_metadata(path: Path, url: str, cached: bool) -> dict[str, Any]:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return {
        "file": str(path.relative_to(ROOT)),
        "url": url,
        "downloaded_at": datetime.now().isoformat(timespec="seconds"),
        "sha256": sha.hexdigest(),
        "bytes": path.stat().st_size,
        "cached": cached,
    }


def sniff_delimiter(sample: str) -> str:
    return ";" if sample.count(";") >= sample.count(",") else ","


def iter_csv_rows_from_handle(handle: TextIO, delimiter: str | None = None) -> Iterator[dict[str, str]]:
    pos = handle.tell()
    sample = handle.read(8192)
    handle.seek(pos)
    reader = csv.DictReader(handle, delimiter=delimiter or sniff_delimiter(sample))
    for row in reader:
        yield {(k or "").strip(): (v or "").strip() for k, v in row.items()}


def read_csv_rows(path: Path, limit: int | None = None) -> tuple[list[dict[str, str]], list[str]]:
    raw = path.read_bytes()[:8192]
    sample = raw.decode("utf-8-sig", errors="ignore")
    delimiter = sniff_delimiter(sample)
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows = []
        for idx, row in enumerate(reader):
            if limit is not None and idx >= limit:
                break
            rows.append({(k or "").strip(): (v or "").strip() for k, v in row.items()})
        return rows, reader.fieldnames or []


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    text = text.replace(".", "").replace(",", ".") if "," in text else text
    try:
        return float(text)
    except ValueError:
        return None


def first_present(row: dict[str, Any], candidates: list[str]) -> Any:
    lower = {k.lower(): k for k in row}
    for candidate in candidates:
        key = lower.get(candidate.lower())
        if key is not None and row.get(key) not in {"", None}:
            return row[key]
    return ""
