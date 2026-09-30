"""Fetch raw daily price data and provenance metadata."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

import httpx

from risk_monitor.config import (
    ASSETS,
    END_DATE,
    METADATA_DIR,
    NASDAQ_HISTORICAL_URL_TEMPLATE,
    RAW_DATA_DIR,
    START_DATE,
    AssetConfig,
)

REQUIRED_COLUMNS = ("Date", "Open", "High", "Low", "Close", "Volume")
NASDAQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 financial-risk-monitor/0.1",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
}


@dataclass(frozen=True)
class FetchResult:
    """Provenance for one raw source file."""

    symbol: str
    source_url: str
    fetched_at_utc: str
    requested_start_date: str
    requested_end_date: str
    output_path: str
    sha256: str
    row_count: int
    first_date: str | None
    last_date: str | None
    columns: list[str]


def build_nasdaq_url(symbol: str, start_date: str, end_date: str) -> str:
    """Build a reproducible Nasdaq historical quote API URL."""

    base_url = NASDAQ_HISTORICAL_URL_TEMPLATE.format(symbol=symbol)
    return (
        f"{base_url}?assetclass=etf&fromdate={start_date}"
        f"&todate={end_date}&limit=9999"
    )


def clean_number(value: str | float | None) -> str:
    """Normalize Nasdaq number strings for CSV output."""

    if value is None:
        return ""
    return str(value).replace("$", "").replace(",", "").strip()


def parse_nasdaq_date(date_text: str) -> str:
    """Convert Nasdaq MM/DD/YYYY dates to ISO YYYY-MM-DD dates."""

    return datetime.strptime(date_text, "%m/%d/%Y").replace(tzinfo=UTC).date().isoformat()


def rows_to_csv(rows: list[dict[str, str]]) -> str:
    """Serialize normalized rows to CSV text."""

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=REQUIRED_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def normalize_nasdaq_rows(payload: dict) -> list[dict[str, str]]:
    """Extract and normalize historical OHLCV rows from Nasdaq JSON."""

    try:
        rows = payload["data"]["tradesTable"]["rows"]
    except KeyError as exc:
        raise ValueError("Nasdaq response did not contain tradesTable rows") from exc

    normalized = [
        {
            "Date": parse_nasdaq_date(row["date"]),
            "Open": clean_number(row.get("open")),
            "High": clean_number(row.get("high")),
            "Low": clean_number(row.get("low")),
            "Close": clean_number(row.get("close")),
            "Volume": clean_number(row.get("volume")),
        }
        for row in rows
    ]
    return sorted(normalized, key=lambda row: row["Date"])


def parse_csv_summary(csv_text: str) -> tuple[int, str | None, str | None, list[str]]:
    """Return row count, first date, last date, and columns from CSV text."""

    rows = list(csv.DictReader(csv_text.splitlines()))
    if not rows:
        return 0, None, None, []

    columns = list(rows[0].keys())
    return len(rows), rows[0].get("Date"), rows[-1].get("Date"), columns


def fetch_asset(
    asset: AssetConfig,
    *,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
    raw_dir: Path = RAW_DATA_DIR,
    timeout_seconds: float = 30.0,
) -> FetchResult:
    """Fetch one asset from Nasdaq and write the raw normalized CSV file."""

    raw_dir.mkdir(parents=True, exist_ok=True)
    url = build_nasdaq_url(asset.symbol, start_date, end_date)
    response = httpx.get(
        url,
        timeout=timeout_seconds,
        follow_redirects=True,
        headers=NASDAQ_HEADERS,
    )
    response.raise_for_status()

    rows = normalize_nasdaq_rows(response.json())
    csv_text = rows_to_csv(rows)
    row_count, first_date, last_date, columns = parse_csv_summary(csv_text)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    if row_count == 0 or missing_columns:
        raise ValueError(
            f"Unexpected Nasdaq response for {asset.symbol}: "
            f"row_count={row_count}, missing_columns={missing_columns}"
        )

    output_path = raw_dir / f"{asset.symbol.lower()}_daily_nasdaq.csv"
    output_path.write_text(csv_text, encoding="utf-8")
    sha256 = hashlib.sha256(output_path.read_bytes()).hexdigest()

    return FetchResult(
        symbol=asset.symbol,
        source_url=url,
        fetched_at_utc=datetime.now(UTC).isoformat(timespec="seconds"),
        requested_start_date=start_date,
        requested_end_date=end_date,
        output_path=str(output_path),
        sha256=sha256,
        row_count=row_count,
        first_date=first_date,
        last_date=last_date,
        columns=columns,
    )


def fetch_all_assets(
    *,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
    raw_dir: Path = RAW_DATA_DIR,
    metadata_dir: Path = METADATA_DIR,
) -> list[FetchResult]:
    """Fetch all configured project assets and write provenance metadata."""

    metadata_dir.mkdir(parents=True, exist_ok=True)
    results = [
        fetch_asset(asset, start_date=start_date, end_date=end_date, raw_dir=raw_dir)
        for asset in ASSETS
    ]
    metadata = {
        "source": "Nasdaq historical quote API",
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_change_note": (
            "Stooq was planned in Phase 1, but the CSV endpoint returned a browser "
            "verification page followed by Access denied during Phase 2 Step 1."
        ),
        "assets": [asdict(asset) for asset in ASSETS],
        "fetches": [asdict(result) for result in results],
    }
    metadata_path = metadata_dir / "raw_fetch_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return results
