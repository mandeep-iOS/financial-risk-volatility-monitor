"""Store validated prices and returns in a reproducible SQLite database."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from risk_monitor.config import (
    ASSETS,
    DATABASE_PATH,
    METADATA_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)
from risk_monitor.features import RETURN_COLUMN
from risk_monitor.validation import load_raw_prices


@dataclass(frozen=True)
class StoredSymbolSummary:
    """Row-count and date-range summary for one stored symbol."""

    symbol: str
    price_rows: int
    return_rows: int
    first_price_date: str
    last_price_date: str
    first_return_date: str
    last_return_date: str


@dataclass(frozen=True)
class StoreBuildResult:
    """Metadata for a SQLite store build."""

    database_path: str
    created_at_utc: str
    sha256: str
    symbols: list[StoredSymbolSummary]


def sha256_file(path: Path) -> str:
    """Calculate a SHA-256 digest for a local file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_returns(path: Path) -> pd.DataFrame:
    """Load one processed return CSV."""

    return pd.read_csv(path, parse_dates=["Date"])


def normalized_prices(symbol: str, path: Path) -> pd.DataFrame:
    """Load and normalize one symbol's validated price rows for storage."""

    prices = load_raw_prices(path).sort_values("Date").copy()
    prices.insert(0, "Symbol", symbol)
    prices["Date"] = prices["Date"].dt.date.astype(str)
    for column in ["Open", "High", "Low", "Close", "Volume"]:
        prices[column] = pd.to_numeric(prices[column], errors="raise")
    return prices[["Symbol", "Date", "Open", "High", "Low", "Close", "Volume"]]


def normalized_returns(symbol: str, path: Path) -> pd.DataFrame:
    """Load and normalize one symbol's return rows for storage."""

    returns = load_returns(path).sort_values("Date").copy()
    returns.insert(0, "Symbol", symbol)
    returns["Date"] = returns["Date"].dt.date.astype(str)
    returns["Close"] = pd.to_numeric(returns["Close"], errors="raise")
    returns[RETURN_COLUMN] = pd.to_numeric(returns[RETURN_COLUMN], errors="raise")
    return returns[["Symbol", "Date", "Close", RETURN_COLUMN]]


def initialize_schema(connection: sqlite3.Connection) -> None:
    """Create the SQLite schema for validated project data."""

    connection.executescript(
        """
        DROP TABLE IF EXISTS prices;
        DROP TABLE IF EXISTS returns;
        DROP TABLE IF EXISTS provenance;

        CREATE TABLE prices (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            PRIMARY KEY (symbol, date)
        );

        CREATE TABLE returns (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            close REAL NOT NULL,
            return_pct REAL NOT NULL,
            PRIMARY KEY (symbol, date)
        );

        CREATE TABLE provenance (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )


def write_frame(connection: sqlite3.Connection, table: str, frame: pd.DataFrame) -> None:
    """Append a DataFrame into SQLite using lowercase column names."""

    db_frame = frame.rename(columns={column: column.lower() for column in frame.columns})
    db_frame = db_frame.rename(columns={RETURN_COLUMN.lower(): "return_pct"})
    db_frame.to_sql(table, connection, if_exists="append", index=False)


def summarize_symbol(symbol: str, prices: pd.DataFrame, returns: pd.DataFrame) -> StoredSymbolSummary:
    """Build a row-count and date-range summary for one symbol."""

    return StoredSymbolSummary(
        symbol=symbol,
        price_rows=len(prices),
        return_rows=len(returns),
        first_price_date=str(prices["Date"].iloc[0]),
        last_price_date=str(prices["Date"].iloc[-1]),
        first_return_date=str(returns["Date"].iloc[0]),
        last_return_date=str(returns["Date"].iloc[-1]),
    )


def build_sqlite_store(
    *,
    database_path: Path = DATABASE_PATH,
    raw_dir: Path = RAW_DATA_DIR,
    processed_dir: Path = PROCESSED_DATA_DIR,
    metadata_dir: Path = METADATA_DIR,
) -> StoreBuildResult:
    """Build the SQLite store from validated raw prices and processed returns."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()

    created_at_utc = datetime.now(UTC).isoformat(timespec="seconds")
    summaries: list[StoredSymbolSummary] = []
    provenance = {
        "created_at_utc": created_at_utc,
        "source": "Validated Nasdaq OHLCV prices and calculated close-to-close returns.",
        "return_units": "percent",
        "adjustment_note": (
            "Returns use raw Close prices and are not total returns or dividend-adjusted returns."
        ),
    }

    with sqlite3.connect(database_path) as connection:
        initialize_schema(connection)
        for asset in ASSETS:
            price_path = raw_dir / f"{asset.symbol.lower()}_daily_nasdaq.csv"
            return_path = processed_dir / f"{asset.symbol.lower()}_daily_returns.csv"
            prices = normalized_prices(asset.symbol, price_path)
            returns = normalized_returns(asset.symbol, return_path)

            write_frame(connection, "prices", prices)
            write_frame(connection, "returns", returns)
            summaries.append(summarize_symbol(asset.symbol, prices, returns))

            provenance[f"{asset.symbol.lower()}_raw_price_path"] = str(price_path)
            provenance[f"{asset.symbol.lower()}_raw_price_sha256"] = sha256_file(price_path)
            provenance[f"{asset.symbol.lower()}_return_path"] = str(return_path)
            provenance[f"{asset.symbol.lower()}_return_sha256"] = sha256_file(return_path)

        for key, value in provenance.items():
            connection.execute(
                "INSERT INTO provenance (key, value) VALUES (?, ?)",
                (key, str(value)),
            )

    result = StoreBuildResult(
        database_path=str(database_path),
        created_at_utc=created_at_utc,
        sha256=sha256_file(database_path),
        symbols=summaries,
    )
    metadata = {
        **asdict(result),
        "tables": {
            "prices": "Validated daily OHLCV rows keyed by symbol and date.",
            "returns": "Daily close-to-close percentage returns keyed by symbol and date.",
            "provenance": "Source paths, source checksums, units, and adjustment notes.",
        },
    }
    metadata_path = metadata_dir / "sqlite_store_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return result

