"""Five-trading-day variance and volatility forecasts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pandas_market_calendars as mcal

from risk_monitor.baseline import BASELINE_WINDOW
from risk_monitor.config import DATABASE_PATH, METADATA_DIR
from risk_monitor.garch import fit_garch
from risk_monitor.volatility import load_returns

FORECAST_HORIZON = 5


@dataclass(frozen=True)
class ForecastRow:
    """One model and horizon forecast row."""

    symbol: str
    forecast_date: str
    horizon: int
    model: str
    variance_pct2: float
    volatility_pct: float
    training_end_date: str


def next_trading_dates(last_date: pd.Timestamp, horizon: int = FORECAST_HORIZON) -> list[pd.Timestamp]:
    """Return the next NYSE sessions after the latest observed date."""

    calendar = mcal.get_calendar("NYSE")
    schedule = calendar.schedule(
        start_date=(last_date + pd.Timedelta(days=1)).date(),
        end_date=(last_date + pd.Timedelta(days=20)).date(),
    )
    return [pd.Timestamp(value).normalize() for value in schedule.index[:horizon]]


def create_five_day_forecast(
    returns: pd.DataFrame,
    *,
    symbol: str,
    horizon: int = FORECAST_HORIZON,
) -> list[ForecastRow]:
    """Create baseline and GARCH forecasts from all data through the latest date."""

    if horizon < 1:
        raise ValueError("Forecast horizon must be at least 1 trading day")
    symbol_returns = returns[returns["symbol"] == symbol].sort_values("date")
    if len(symbol_returns) < BASELINE_WINDOW:
        raise ValueError("Five-day forecast requires at least 20 returns")
    training_end = symbol_returns["date"].max()
    dates = next_trading_dates(training_end, horizon)
    baseline_variance = float(symbol_returns["return_pct"].tail(BASELINE_WINDOW).var(ddof=1))
    garch_result, _ = fit_garch(returns, symbol=symbol, training_end=training_end)
    garch_variances = garch_result.forecast(horizon=horizon, reindex=False).variance.iloc[-1].to_numpy()
    rows: list[ForecastRow] = []
    for index, date in enumerate(dates):
        for model, variance in (("baseline", baseline_variance), ("garch", float(garch_variances[index]))):
            rows.append(
                ForecastRow(
                    symbol=symbol,
                    forecast_date=date.date().isoformat(),
                    horizon=index + 1,
                    model=model,
                    variance_pct2=float(variance),
                    volatility_pct=float(np.sqrt(variance)),
                    training_end_date=training_end.date().isoformat(),
                )
            )
    return rows


def forecast_all_symbols(
    *,
    database_path: Path = DATABASE_PATH,
    metadata_dir: Path = METADATA_DIR,
) -> list[ForecastRow]:
    """Create and save the five-session forecast for every stored symbol."""

    returns = load_returns(database_path)
    rows: list[ForecastRow] = []
    for symbol in sorted(returns["symbol"].unique()):
        rows.extend(create_five_day_forecast(returns, symbol=symbol))
    metadata_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "database_path": str(database_path),
        "horizon_sessions": FORECAST_HORIZON,
        "variance_units": "percentage-points-squared",
        "volatility_units": "percentage points",
        "forecasts": [asdict(row) for row in rows],
    }
    (metadata_dir / "five_day_forecast.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return rows
