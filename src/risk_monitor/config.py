"""Project configuration values."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
DATABASE_PATH = PROCESSED_DATA_DIR / "risk_monitor.sqlite"
FIGURES_DIR = PROJECT_ROOT / "docs" / "figures"


@dataclass(frozen=True)
class AssetConfig:
    """Source metadata for one project asset."""

    symbol: str
    name: str
    market: str


ASSETS: tuple[AssetConfig, ...] = (
    AssetConfig(
        symbol="SPY",
        name="SPDR S&P 500 ETF Trust",
        market="US equities",
    ),
    AssetConfig(
        symbol="QQQ",
        name="Invesco QQQ Trust, Series 1",
        market="US equities",
    ),
)

START_DATE = "2015-01-02"
END_DATE = "2025-12-31"
NASDAQ_HISTORICAL_URL_TEMPLATE = "https://api.nasdaq.com/api/quote/{symbol}/historical"
