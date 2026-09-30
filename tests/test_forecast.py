import pandas as pd
import pytest

from risk_monitor.forecast import create_five_day_forecast, next_trading_dates


def test_next_trading_dates_skips_weekend() -> None:
    dates = next_trading_dates(pd.Timestamp("2025-01-03"), horizon=2)
    assert [date.date().isoformat() for date in dates] == ["2025-01-06", "2025-01-07"]


def test_five_day_forecast_has_separate_units(monkeypatch) -> None:
    dates = pd.date_range("2025-01-02", periods=30, freq="B")
    returns = pd.DataFrame(
        {"symbol": ["SPY"] * 30, "date": dates, "return_pct": [1.0] * 30}
    )
    monkeypatch.setattr(
        "risk_monitor.forecast.fit_garch",
        lambda returns, symbol, training_end: (FakeGarchResult(), returns),
    )

    rows = create_five_day_forecast(returns, symbol="SPY", horizon=2)

    assert len(rows) == 4
    assert {row.model for row in rows} == {"baseline", "garch"}
    assert all(row.volatility_pct == pytest.approx(row.variance_pct2**0.5) for row in rows)


class FakeGarchResult:
    def forecast(self, horizon: int, reindex: bool):
        class Forecast:
            variance = pd.DataFrame([[4.0] * horizon])

        return Forecast()
