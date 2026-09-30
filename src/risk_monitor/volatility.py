"""Exploratory rolling-volatility and return-dependence analysis."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from risk_monitor.config import DATABASE_PATH, FIGURES_DIR, METADATA_DIR

TRADING_DAYS_PER_YEAR = 252
ROLLING_WINDOWS = (20, 50)


@dataclass(frozen=True)
class VolatilityFigureResult:
    """Metadata for one volatility analysis figure."""

    name: str
    path: str
    symbols: list[str]
    first_date: str
    last_date: str
    units: str


def load_returns(database_path: Path = DATABASE_PATH) -> pd.DataFrame:
    """Load stored returns in symbol/date order using a read-only connection."""

    with sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        frame = pd.read_sql_query(
            "SELECT symbol, date, return_pct FROM returns",
            connection,
            parse_dates=["date"],
        )
    return frame.sort_values(["symbol", "date"]).reset_index(drop=True)


def calculate_rolling_volatility(
    returns: pd.DataFrame,
    windows: tuple[int, ...] = ROLLING_WINDOWS,
) -> pd.DataFrame:
    """Calculate annualized rolling volatility in percentage points."""

    required = {"symbol", "date", "return_pct"}
    missing = required.difference(returns.columns)
    if missing:
        raise ValueError(f"Missing return columns: {sorted(missing)}")
    if any(window < 2 for window in windows):
        raise ValueError("Rolling windows must be at least 2 sessions")

    ordered = returns.sort_values(["symbol", "date"]).copy()
    grouped = ordered.groupby("symbol", sort=False)["return_pct"]
    for window in windows:
        ordered[f"volatility_{window}d"] = (
            grouped.transform(lambda series, window=window: series.rolling(window).std(ddof=1))
            * TRADING_DAYS_PER_YEAR**0.5
        )
    return ordered


def _date_range(frame: pd.DataFrame) -> tuple[str, str]:
    return frame["date"].min().date().isoformat(), frame["date"].max().date().isoformat()


def _save(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=(0, 0.05, 1, 0.95))
    plt.savefig(path, dpi=160)
    plt.close()


def plot_rolling_volatility(frame: pd.DataFrame, output_path: Path) -> VolatilityFigureResult:
    """Plot annualized rolling volatility for each symbol and window."""

    first_date, last_date = _date_range(frame)
    symbols = sorted(frame["symbol"].unique().tolist())
    fig, axes = plt.subplots(len(symbols), 1, figsize=(11, 7), sharex=True, sharey=True, squeeze=False)
    for index, symbol in enumerate(symbols):
        subset = frame[frame["symbol"] == symbol]
        ax = axes[index, 0]
        for window, color in zip(ROLLING_WINDOWS, ("C0", "C1")):
            ax.plot(subset["date"], subset[f"volatility_{window}d"], label=f"{window}-day", color=color)
        ax.set_ylabel("Annualized volatility (%)")
        ax.legend(loc="upper right")
        ax.set_title(symbol, loc="left", fontsize=10)
    fig.suptitle(f"Annualized Rolling Volatility ({first_date} to {last_date})")
    axes[-1, 0].set_xlabel("Date")
    fig.text(0.01, 0.01, "Source: Nasdaq historical quote API; volatility uses raw Close returns", fontsize=8)
    _save(output_path)
    return VolatilityFigureResult("rolling_volatility", str(output_path), symbols, first_date, last_date, "annualized percent")


def plot_squared_return_dependence(
    returns: pd.DataFrame,
    output_path: Path,
    lags: int = 20,
) -> VolatilityFigureResult:
    """Plot ACF and PACF of squared daily percentage returns."""

    first_date, last_date = _date_range(returns)
    symbols = sorted(returns["symbol"].unique().tolist())
    fig, axes = plt.subplots(len(symbols), 2, figsize=(11, 3.5 * len(symbols)), squeeze=False)
    for index, symbol in enumerate(symbols):
        values = returns.loc[returns["symbol"] == symbol, "return_pct"].pow(2).dropna()
        plot_acf(values, lags=lags, ax=axes[index, 0], title=f"{symbol}: ACF")
        pacf_lags = min(lags, (len(values) // 2) - 1)
        plot_pacf(values, lags=pacf_lags, ax=axes[index, 1], method="ywm", title=f"{symbol}: PACF")
    fig.suptitle(f"Dependence in Squared Daily Returns ({first_date} to {last_date})")
    fig.text(0.01, 0.01, "Squared returns are in percentage-squared units; bands are approximate 95% intervals", fontsize=8)
    _save(output_path)
    return VolatilityFigureResult("squared_return_acf_pacf", str(output_path), symbols, first_date, last_date, "return percent squared")


def create_volatility_analysis(
    *,
    database_path: Path = DATABASE_PATH,
    figures_dir: Path = FIGURES_DIR,
    metadata_dir: Path = METADATA_DIR,
) -> list[VolatilityFigureResult]:
    """Create Step 7 rolling-volatility and squared-return diagnostics."""

    returns = load_returns(database_path)
    rolling = calculate_rolling_volatility(returns)
    results = [
        plot_rolling_volatility(rolling, figures_dir / "rolling_volatility.png"),
        plot_squared_return_dependence(returns, figures_dir / "squared_return_acf_pacf.png"),
    ]
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "database_path": str(database_path),
        "annualization_factor": TRADING_DAYS_PER_YEAR,
        "rolling_windows": list(ROLLING_WINDOWS),
        "acf_pacf_lags": 20,
        "figures": [asdict(result) for result in results],
    }
    (metadata_dir / "volatility_analysis_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return results
