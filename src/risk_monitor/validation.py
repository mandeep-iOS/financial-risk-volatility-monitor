"""Validate raw price files before feature engineering."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pandas_market_calendars as mcal

from risk_monitor.config import ASSETS, METADATA_DIR, RAW_DATA_DIR
from risk_monitor.data_fetch import REQUIRED_COLUMNS

PRICE_COLUMNS = ("Open", "High", "Low", "Close")
VOLUME_COLUMNS = ("Volume",)


@dataclass(frozen=True)
class PriceValidationResult:
    """Validation result for one raw price file."""

    symbol: str
    path: str
    status: str
    row_count: int
    first_date: str | None
    last_date: str | None
    missing_columns: list[str]
    extra_columns: list[str]
    duplicate_dates: list[str]
    non_chronological_dates: bool
    missing_required_values: dict[str, int]
    nonpositive_values: dict[str, int]
    invalid_ohlc_rows: int
    expected_sessions: int
    missing_sessions: list[str]
    unexpected_sessions: list[str]


def expected_trading_sessions(start_date: str, end_date: str) -> pd.DatetimeIndex:
    """Return expected NYSE trading-session dates for the data range."""

    calendar = mcal.get_calendar("NYSE")
    schedule = calendar.schedule(start_date=start_date, end_date=end_date)
    return pd.DatetimeIndex(schedule.index).normalize()


def load_raw_prices(path: Path) -> pd.DataFrame:
    """Load one raw price CSV with parsed dates."""

    return pd.read_csv(path, parse_dates=["Date"])


def validate_price_file(symbol: str, path: Path) -> PriceValidationResult:
    """Validate one raw OHLCV CSV file."""

    df = load_raw_prices(path)
    columns = list(df.columns)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    extra_columns = [column for column in columns if column not in REQUIRED_COLUMNS]

    if missing_columns:
        return PriceValidationResult(
            symbol=symbol,
            path=str(path),
            status="fail",
            row_count=len(df),
            first_date=None,
            last_date=None,
            missing_columns=missing_columns,
            extra_columns=extra_columns,
            duplicate_dates=[],
            non_chronological_dates=False,
            missing_required_values={},
            nonpositive_values={},
            invalid_ohlc_rows=0,
            expected_sessions=0,
            missing_sessions=[],
            unexpected_sessions=[],
        )

    date_series = df["Date"]
    date_strings = date_series.dt.date.astype(str)
    first_date = date_series.min().date().isoformat() if len(df) else None
    last_date = date_series.max().date().isoformat() if len(df) else None

    duplicate_dates = sorted(date_strings[date_series.duplicated()].unique().tolist())
    non_chronological_dates = not date_series.is_monotonic_increasing

    missing_required_values = {
        column: int(df[column].isna().sum()) for column in REQUIRED_COLUMNS
    }

    numeric_columns = [*PRICE_COLUMNS, *VOLUME_COLUMNS]
    numeric_df = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    nonpositive_values = {
        column: int((numeric_df[column] <= 0).sum()) for column in numeric_columns
    }
    missing_required_values.update(
        {
            column: missing_required_values[column] + int(numeric_df[column].isna().sum())
            for column in numeric_columns
        }
    )

    invalid_ohlc_rows = int(
        (
            (numeric_df["High"] < numeric_df["Low"])
            | (numeric_df["Open"] > numeric_df["High"])
            | (numeric_df["Open"] < numeric_df["Low"])
            | (numeric_df["Close"] > numeric_df["High"])
            | (numeric_df["Close"] < numeric_df["Low"])
        ).sum()
    )

    if first_date and last_date:
        expected_sessions_index = expected_trading_sessions(first_date, last_date)
    else:
        expected_sessions_index = pd.DatetimeIndex([])
    actual_sessions_index = pd.DatetimeIndex(date_series).normalize()

    expected_set = set(expected_sessions_index.date.astype(str))
    actual_set = set(actual_sessions_index.date.astype(str))
    missing_sessions = sorted(expected_set - actual_set)
    unexpected_sessions = sorted(actual_set - expected_set)

    errors_present = any(
        [
            missing_columns,
            duplicate_dates,
            non_chronological_dates,
            any(count > 0 for count in missing_required_values.values()),
            any(count > 0 for count in nonpositive_values.values()),
            invalid_ohlc_rows > 0,
            unexpected_sessions,
        ]
    )
    status = "fail" if errors_present else "pass"

    return PriceValidationResult(
        symbol=symbol,
        path=str(path),
        status=status,
        row_count=len(df),
        first_date=first_date,
        last_date=last_date,
        missing_columns=missing_columns,
        extra_columns=extra_columns,
        duplicate_dates=duplicate_dates,
        non_chronological_dates=non_chronological_dates,
        missing_required_values=missing_required_values,
        nonpositive_values=nonpositive_values,
        invalid_ohlc_rows=invalid_ohlc_rows,
        expected_sessions=len(expected_sessions_index),
        missing_sessions=missing_sessions,
        unexpected_sessions=unexpected_sessions,
    )


def validate_all_prices(
    *,
    raw_dir: Path = RAW_DATA_DIR,
    metadata_dir: Path = METADATA_DIR,
) -> list[PriceValidationResult]:
    """Validate all configured raw price files and write a JSON report."""

    metadata_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for asset in ASSETS:
        path = raw_dir / f"{asset.symbol.lower()}_daily_nasdaq.csv"
        results.append(validate_price_file(asset.symbol, path))

    report = {
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "calendar": "NYSE",
        "checks": [
            "required schema",
            "chronological dates",
            "duplicate dates",
            "missing required values",
            "nonpositive OHLCV values",
            "OHLC internal consistency",
            "missing and unexpected trading sessions",
        ],
        "results": [asdict(result) for result in results],
    }
    report_path = metadata_dir / "price_validation_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return results

