import pandas as pd
import pytest

from risk_monitor.baseline import historical_variance_forecasts


def test_baseline_excludes_target_return() -> None:
    returns = pd.DataFrame(
        {
            "symbol": ["SPY"] * 4,
            "date": pd.date_range("2024-02-20", periods=4),
            "return_pct": [1.0, 2.0, 3.0, 100.0],
        }
    )

    forecasts = historical_variance_forecasts(
        returns, window=2, target_start=pd.Timestamp("2024-02-22")
    )

    # The 2024-02-22 forecast uses 1 and 2, excluding its target return of 3.
    assert forecasts.iloc[0]["forecast_variance_pct2"] == 0.5
    # The 100% target return is not included in its own forecast either.
    assert forecasts.iloc[1]["forecast_variance_pct2"] == 0.5


def test_baseline_rejects_invalid_window() -> None:
    returns = pd.DataFrame({"symbol": ["SPY"], "date": pd.Timestamp("2024-01-01"), "return_pct": [1.0]})
    with pytest.raises(ValueError, match="at least 2"):
        historical_variance_forecasts(returns, window=1)
