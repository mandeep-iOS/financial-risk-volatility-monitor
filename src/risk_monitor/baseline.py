"""Historical-variance baseline for one-day-ahead forecasts."""

from __future__ import annotations

import pandas as pd

from risk_monitor.split import TEST_START_DATE

BASELINE_WINDOW = 20
VARIANCE_COLUMN = "forecast_variance_pct2"


def historical_variance_forecasts(
    returns: pd.DataFrame,
    *,
    window: int = BASELINE_WINDOW,
    target_start: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Forecast target-date variance from the preceding fixed return window.

    Returns are expressed in percentage points, so forecast variance is in
    percentage-points-squared. The shift ensures the target return is excluded.
    """

    required = {"symbol", "date", "return_pct"}
    missing = required.difference(returns.columns)
    if missing:
        raise ValueError(f"Missing baseline columns: {sorted(missing)}")
    if window < 2:
        raise ValueError("Historical variance window must be at least 2 sessions")

    ordered = returns.sort_values(["symbol", "date"]).copy()
    grouped = ordered.groupby("symbol", sort=False)["return_pct"]
    ordered[VARIANCE_COLUMN] = grouped.transform(
        lambda series: series.shift(1).rolling(window).var(ddof=1)
    )
    ordered["forecast_origin"] = ordered["date"] - pd.Timedelta(days=1)
    if target_start is None:
        target_start = TEST_START_DATE
    forecasts = ordered[ordered["date"] >= target_start].copy()
    return forecasts[["symbol", "date", "forecast_origin", VARIANCE_COLUMN]].reset_index(drop=True)
