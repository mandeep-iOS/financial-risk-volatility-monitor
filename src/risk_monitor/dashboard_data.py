"""Symbol-aware data access and freshness contract for the dashboard."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from risk_monitor.config import DATABASE_PATH, METADATA_DIR
from risk_monitor.volatility import calculate_rolling_volatility


@dataclass(frozen=True)
class Freshness:
    """Dates and status labels presented by user-facing views."""

    selected_symbol: str
    latest_available_price_date: date
    latest_return_date: date
    model_training_cutoff: date
    forecast_generated_at_utc: datetime
    forecast_start_date: date
    forecast_end_date: date
    forecast_status: str
    is_current: bool


@dataclass(frozen=True)
class DashboardData:
    """All symbol-aware data required by dashboard sections."""

    selected_symbol: str
    prices: pd.DataFrame
    returns: pd.DataFrame
    rolling_volatility: pd.DataFrame
    drawdowns: pd.DataFrame
    forecasts: pd.DataFrame
    scores: pd.DataFrame
    freshness: Freshness


@dataclass(frozen=True)
class AssetSummary:
    """Selected-asset metrics used by the Overview section."""

    latest_close: float
    latest_price_date: date
    recent_5d_return_pct: float
    recent_20d_return_pct: float
    volatility_20d_pct: float
    volatility_50d_pct: float
    current_drawdown_pct: float
    max_drawdown_pct: float
    worst_daily_return_pct: float


@dataclass(frozen=True)
class ComparisonSummary:
    """Comparable risk and return measures for one symbol and date range."""

    symbol: str
    cumulative_return_pct: float
    annualized_volatility_pct: float
    max_drawdown_pct: float
    current_drawdown_pct: float
    worst_daily_return_pct: float
    downside_days: int


@dataclass(frozen=True)
class ScenarioResult:
    """Dollar impact for one arithmetic return scenario."""

    label: str
    move_pct: float
    dollar_impact: float


def _read_table(database_path: Path, table: str, columns: str) -> pd.DataFrame:
    """Read a known SQLite table in read-only mode."""

    if table not in {"prices", "returns"}:
        raise ValueError(f"Unsupported dashboard table: {table}")
    with sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
        return pd.read_sql_query(f"SELECT {columns} FROM {table}", connection, parse_dates=["date"])


def load_prices(database_path: Path = DATABASE_PATH, symbol: str | None = None) -> pd.DataFrame:
    """Load daily prices, optionally filtered to one symbol."""

    frame = _read_table(database_path, "prices", "symbol, date, open, high, low, close, volume")
    return _filter_symbol(frame, symbol)


def load_returns(database_path: Path = DATABASE_PATH, symbol: str | None = None) -> pd.DataFrame:
    """Load daily returns, optionally filtered to one symbol."""

    frame = _read_table(database_path, "returns", "symbol, date, close, return_pct")
    return _filter_symbol(frame, symbol)


def _filter_symbol(frame: pd.DataFrame, symbol: str | None) -> pd.DataFrame:
    if symbol is not None:
        symbol = symbol.upper()
        if symbol not in set(frame["symbol"]):
            raise ValueError(f"Unknown symbol: {symbol}")
        frame = frame[frame["symbol"] == symbol]
    sort_columns = ["symbol", "date"] if "date" in frame else ["symbol", "forecast_date"]
    return frame.sort_values(sort_columns).reset_index(drop=True)


def load_rolling_volatility(
    database_path: Path = DATABASE_PATH,
    symbol: str | None = None,
) -> pd.DataFrame:
    """Load returns with annualized 20- and 50-session volatility columns."""

    return calculate_rolling_volatility(load_returns(database_path, symbol))


def load_drawdowns(database_path: Path = DATABASE_PATH, symbol: str | None = None) -> pd.DataFrame:
    """Calculate drawdown from each symbol's running close-price peak."""

    prices = load_prices(database_path, symbol)
    prices = prices.copy()
    prices["running_peak"] = prices.groupby("symbol")["close"].cummax()
    prices["drawdown_pct"] = (prices["close"] / prices["running_peak"] - 1) * 100
    return prices[["symbol", "date", "close", "running_peak", "drawdown_pct"]]


def load_forecasts(
    forecast_path: Path = METADATA_DIR / "five_day_forecast.json",
    symbol: str | None = None,
) -> pd.DataFrame:
    """Load five-session forecasts, optionally filtered to one symbol."""

    payload = json.loads(forecast_path.read_text(encoding="utf-8"))
    frame = pd.DataFrame(payload["forecasts"])
    frame["forecast_date"] = pd.to_datetime(frame["forecast_date"])
    frame["training_end_date"] = pd.to_datetime(frame["training_end_date"])
    return _filter_symbol(frame, symbol)


def load_scores(
    scores_path: Path = METADATA_DIR / "forecast_scores.json",
    symbol: str | None = None,
) -> pd.DataFrame:
    """Load model scores, optionally filtered to one symbol."""

    payload = json.loads(scores_path.read_text(encoding="utf-8"))
    frame = pd.DataFrame(payload["scores"])
    if symbol is not None:
        selected = symbol.upper()
        if selected not in set(frame["symbol"]) - {"ALL"}:
            raise ValueError(f"Unknown symbol: {selected}")
        frame = frame[frame["symbol"].isin([selected, "ALL"])]
    return frame.reset_index(drop=True)


def load_backtest_forecasts(
    forecast_path: Path = METADATA_DIR / "rolling_forecasts.csv",
    symbol: str | None = None,
) -> pd.DataFrame:
    """Load aligned backtest forecasts for evidence and date-range labels."""

    frame = pd.read_csv(forecast_path, parse_dates=["target_date", "forecast_origin"])
    return _filter_symbol(frame, symbol)


def load_freshness(
    *,
    database_path: Path = DATABASE_PATH,
    forecast_path: Path = METADATA_DIR / "five_day_forecast.json",
    symbol: str,
    as_of: date | None = None,
) -> Freshness:
    """Build an explicit freshness contract for a selected symbol."""

    prices = load_prices(database_path, symbol)
    returns = load_returns(database_path, symbol)
    payload = json.loads(forecast_path.read_text(encoding="utf-8"))
    forecasts = load_forecasts(forecast_path, symbol)
    latest_price = prices["date"].max().date()
    latest_return = returns["date"].max().date()
    training_cutoff = forecasts["training_end_date"].max().date()
    generated_at = datetime.fromisoformat(payload["created_at_utc"])
    today = as_of or datetime.now(UTC).date()
    is_current = latest_price >= today
    return Freshness(
        selected_symbol=symbol.upper(),
        latest_available_price_date=latest_price,
        latest_return_date=latest_return,
        model_training_cutoff=training_cutoff,
        forecast_generated_at_utc=generated_at,
        forecast_start_date=forecasts["forecast_date"].min().date(),
        forecast_end_date=forecasts["forecast_date"].max().date(),
        forecast_status="current" if is_current else "historical/example",
        is_current=is_current,
    )


def load_dashboard_data(
    symbol: str,
    *,
    database_path: Path = DATABASE_PATH,
    forecast_path: Path = METADATA_DIR / "five_day_forecast.json",
    scores_path: Path = METADATA_DIR / "forecast_scores.json",
    as_of: date | None = None,
) -> DashboardData:
    """Load all symbol-aware dashboard data and freshness fields."""

    selected = symbol.upper()
    return DashboardData(
        selected_symbol=selected,
        prices=load_prices(database_path, selected),
        returns=load_returns(database_path, selected),
        rolling_volatility=load_rolling_volatility(database_path, selected),
        drawdowns=load_drawdowns(database_path, selected),
        forecasts=load_forecasts(forecast_path, selected),
        scores=load_scores(scores_path, selected),
        freshness=load_freshness(
            database_path=database_path,
            forecast_path=forecast_path,
            symbol=selected,
            as_of=as_of,
        ),
    )


def summarize_asset(data: DashboardData) -> AssetSummary:
    """Calculate selected-asset Overview metrics from symbol-filtered data."""

    returns = data.returns["return_pct"].astype(float)
    latest_volatility = data.rolling_volatility.iloc[-1]
    return AssetSummary(
        latest_close=float(data.prices.iloc[-1]["close"]),
        latest_price_date=data.prices.iloc[-1]["date"].date(),
        recent_5d_return_pct=float(((1 + returns.tail(5) / 100).prod() - 1) * 100),
        recent_20d_return_pct=float(((1 + returns.tail(20) / 100).prod() - 1) * 100),
        volatility_20d_pct=float(latest_volatility["volatility_20d"]),
        volatility_50d_pct=float(latest_volatility["volatility_50d"]),
        current_drawdown_pct=float(data.drawdowns.iloc[-1]["drawdown_pct"]),
        max_drawdown_pct=float(data.drawdowns["drawdown_pct"].min()),
        worst_daily_return_pct=float(returns.min()),
    )


def calculate_scenarios(
    portfolio_value: float,
    *,
    latest_return_pct: float,
    worst_return_pct: float,
) -> list[ScenarioResult]:
    """Calculate labeled dollar scenarios without implying a prediction."""

    if portfolio_value < 0:
        raise ValueError("Portfolio value cannot be negative")
    moves = (
        ("1% move", 1.0),
        ("2% move", 2.0),
        ("Latest daily return", latest_return_pct),
        ("Worst daily return in selected data", worst_return_pct),
    )
    return [
        ScenarioResult(label, move, portfolio_value * move / 100)
        for label, move in moves
    ]


def compare_assets(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    database_path: Path = DATABASE_PATH,
) -> tuple[pd.DataFrame, list[ComparisonSummary]]:
    """Return aligned chart data and comparable metrics for SPY and QQQ."""

    prices = load_prices(database_path)
    returns = load_returns(database_path)
    if start_date is None:
        start_date = prices["date"].min().date()
    if end_date is None:
        end_date = prices["date"].max().date()
    if start_date > end_date:
        raise ValueError("Comparison start date must be on or before end date")
    price_range = prices[prices["date"].dt.date.between(start_date, end_date)].copy()
    return_range = returns[returns["date"].dt.date.between(start_date, end_date)].copy()
    if price_range.empty or return_range.empty:
        available_start = prices["date"].min().date()
        available_end = prices["date"].max().date()
        raise ValueError(
            f"No data available for selected range. Available range is {available_start} to {available_end}."
        )
    price_range["normalized_growth"] = price_range["close"] / price_range.groupby("symbol")["close"].transform("first") * 100
    price_range["running_peak"] = price_range.groupby("symbol")["normalized_growth"].cummax()
    price_range["drawdown_pct"] = price_range["normalized_growth"] / price_range["running_peak"] * 100 - 100
    summaries = []
    for symbol, subset in return_range.groupby("symbol", sort=True):
        prices_for_symbol = price_range[price_range["symbol"] == symbol]
        daily_returns = subset["return_pct"].astype(float)
        drawdowns = prices_for_symbol["drawdown_pct"]
        summaries.append(
            ComparisonSummary(
                symbol=symbol,
                cumulative_return_pct=float(((1 + daily_returns / 100).prod() - 1) * 100),
                annualized_volatility_pct=float(daily_returns.std(ddof=1) * 252**0.5),
                max_drawdown_pct=float(drawdowns.min()),
                current_drawdown_pct=float(drawdowns.iloc[-1]),
                worst_daily_return_pct=float(daily_returns.min()),
                downside_days=int((daily_returns < 0).sum()),
            )
        )
    return price_range, summaries
