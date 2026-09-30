"""Feature engineering for validated price data."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from risk_monitor.config import ASSETS, METADATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR
from risk_monitor.validation import load_raw_prices

RETURN_COLUMN = "ReturnPct"
RETURN_UNITS = "percent"
RETURN_FORMULA = "100 * (Close_t / Close_{t-1} - 1)"


@dataclass(frozen=True)
class ReturnCalculationResult:
    """Metadata for one processed return file."""

    symbol: str
    input_path: str
    output_path: str
    price_column: str
    return_column: str
    return_units: str
    return_formula: str
    input_rows: int
    output_rows: int
    dropped_rows: int
    first_price_date: str
    last_price_date: str
    first_return_date: str
    last_return_date: str


def calculate_returns_frame(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily close-to-close percentage returns from validated prices."""

    ordered = prices.sort_values("Date").copy()
    ordered["Close"] = pd.to_numeric(ordered["Close"], errors="raise")
    ordered[RETURN_COLUMN] = ordered["Close"].pct_change() * 100
    returns = ordered.loc[ordered[RETURN_COLUMN].notna(), ["Date", "Close", RETURN_COLUMN]]
    return returns.reset_index(drop=True)


def calculate_returns_for_file(
    symbol: str,
    input_path: Path,
    output_path: Path,
) -> ReturnCalculationResult:
    """Calculate and write one symbol's processed daily return file."""

    prices = load_raw_prices(input_path)
    returns = calculate_returns_frame(prices)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    returns.to_csv(output_path, index=False, date_format="%Y-%m-%d")

    date_series = prices.sort_values("Date")["Date"]
    return_dates = returns["Date"]
    return ReturnCalculationResult(
        symbol=symbol,
        input_path=str(input_path),
        output_path=str(output_path),
        price_column="Close",
        return_column=RETURN_COLUMN,
        return_units=RETURN_UNITS,
        return_formula=RETURN_FORMULA,
        input_rows=len(prices),
        output_rows=len(returns),
        dropped_rows=len(prices) - len(returns),
        first_price_date=date_series.iloc[0].date().isoformat(),
        last_price_date=date_series.iloc[-1].date().isoformat(),
        first_return_date=return_dates.iloc[0].date().isoformat(),
        last_return_date=return_dates.iloc[-1].date().isoformat(),
    )


def calculate_all_returns(
    *,
    raw_dir: Path = RAW_DATA_DIR,
    processed_dir: Path = PROCESSED_DATA_DIR,
    metadata_dir: Path = METADATA_DIR,
) -> list[ReturnCalculationResult]:
    """Calculate returns for all configured project assets and write metadata."""

    results = []
    for asset in ASSETS:
        input_path = raw_dir / f"{asset.symbol.lower()}_daily_nasdaq.csv"
        output_path = processed_dir / f"{asset.symbol.lower()}_daily_returns.csv"
        results.append(calculate_returns_for_file(asset.symbol, input_path, output_path))

    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "description": "Daily close-to-close price returns calculated from raw Nasdaq Close prices.",
        "return_units": RETURN_UNITS,
        "return_formula": RETURN_FORMULA,
        "adjustment_note": (
            "Returns use raw Close prices and are not total returns or dividend-adjusted returns."
        ),
        "results": [asdict(result) for result in results],
    }
    metadata_path = metadata_dir / "return_calculation_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return results

