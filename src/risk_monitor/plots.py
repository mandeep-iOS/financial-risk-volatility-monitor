"""Exploratory visualizations for validated prices and returns."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from risk_monitor.config import DATABASE_PATH, FIGURES_DIR, METADATA_DIR

SOURCE_LABEL = "Source: Nasdaq historical quote API; returns use raw Close prices"


@dataclass(frozen=True)
class FigureResult:
    """Metadata for one generated figure."""

    name: str
    path: str
    symbols: list[str]
    first_date: str
    last_date: str
    units: str


def load_table(database_path: Path, table: str) -> pd.DataFrame:
    """Load one table from the SQLite store."""

    if table not in {"prices", "returns"}:
        raise ValueError("Chart input must be prices or returns")
    with sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        frame = pd.read_sql_query(f"SELECT * FROM {table}", connection, parse_dates=["date"])
    return frame.sort_values(["symbol", "date"]).reset_index(drop=True)


def date_range(frame: pd.DataFrame) -> tuple[str, str]:
    """Return ISO first and last dates for a frame with a date column."""

    return frame["date"].min().date().isoformat(), frame["date"].max().date().isoformat()


def save_figure(path: Path) -> None:
    """Save the active Matplotlib figure with consistent settings."""

    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=(0, 0.05, 1, 0.95))
    plt.savefig(path, dpi=160)
    plt.close()


def plot_prices(prices: pd.DataFrame, output_path: Path) -> FigureResult:
    """Create a close-price line chart by symbol."""

    first_date, last_date = date_range(prices)
    symbols = sorted(prices["symbol"].unique().tolist())

    plt.figure(figsize=(11, 6))
    for symbol in symbols:
        subset = prices[prices["symbol"] == symbol]
        plt.plot(subset["date"], subset["close"], label=symbol, linewidth=1.5)
    plt.title(f"Daily Close Prices ({first_date} to {last_date})")
    plt.xlabel("Date")
    plt.ylabel("Close price (USD)")
    plt.legend(title="Symbol")
    plt.figtext(0.01, 0.01, SOURCE_LABEL, fontsize=8)
    save_figure(output_path)

    return FigureResult(
        name="daily_close_prices",
        path=str(output_path),
        symbols=symbols,
        first_date=first_date,
        last_date=last_date,
        units="USD",
    )


def plot_returns(returns: pd.DataFrame, output_path: Path) -> FigureResult:
    """Create a daily return line chart by symbol."""

    first_date, last_date = date_range(returns)
    symbols = sorted(returns["symbol"].unique().tolist())

    fig, axes = plt.subplots(len(symbols), 1, figsize=(11, 7), sharex=True,
                             sharey=True, squeeze=False)
    for index, symbol in enumerate(symbols):
        subset = returns[returns["symbol"] == symbol]
        ax = axes[index, 0]
        ax.plot(subset["date"], subset["return_pct"], label=symbol,
                color=f"C{index}", linewidth=0.8)
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set_ylabel("Return (%)")
        ax.legend(loc="upper right")
    fig.suptitle(f"Daily Close-to-Close Price Returns ({first_date} to {last_date})")
    axes[-1, 0].set_xlabel("Date")
    plt.figtext(0.01, 0.01, SOURCE_LABEL, fontsize=8)
    save_figure(output_path)

    return FigureResult(
        name="daily_returns",
        path=str(output_path),
        symbols=symbols,
        first_date=first_date,
        last_date=last_date,
        units="percent",
    )


def plot_return_distributions(returns: pd.DataFrame, output_path: Path) -> FigureResult:
    """Create overlaid return-distribution histograms by symbol."""

    first_date, last_date = date_range(returns)
    symbols = sorted(returns["symbol"].unique().tolist())

    plt.figure(figsize=(11, 6))
    bins = np.histogram_bin_edges(returns["return_pct"], bins=80)
    for symbol in symbols:
        subset = returns[returns["symbol"] == symbol]
        plt.hist(
            subset["return_pct"],
            bins=bins,
            alpha=0.55,
            density=True,
            label=symbol,
        )
    plt.title(f"Distribution of Daily Price Returns ({first_date} to {last_date})")
    plt.xlabel("Daily return (%)")
    plt.ylabel("Density (per percentage point)")
    plt.legend(title="Symbol")
    plt.figtext(0.01, 0.01, SOURCE_LABEL, fontsize=8)
    save_figure(output_path)

    return FigureResult(
        name="return_distributions",
        path=str(output_path),
        symbols=symbols,
        first_date=first_date,
        last_date=last_date,
        units="percent",
    )


def create_exploratory_charts(
    *,
    database_path: Path = DATABASE_PATH,
    figures_dir: Path = FIGURES_DIR,
    metadata_dir: Path = METADATA_DIR,
) -> list[FigureResult]:
    """Create the Phase 2 Step 6 exploratory chart set."""

    prices = load_table(database_path, "prices")
    returns = load_table(database_path, "returns")

    results = [
        plot_prices(prices, figures_dir / "daily_close_prices.png"),
        plot_returns(returns, figures_dir / "daily_returns.png"),
        plot_return_distributions(returns, figures_dir / "return_distributions.png"),
    ]

    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "database_path": str(database_path),
        "source_label": SOURCE_LABEL,
        "figures": [asdict(result) for result in results],
    }
    metadata_path = metadata_dir / "exploratory_figures_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return results
