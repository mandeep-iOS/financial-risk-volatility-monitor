from datetime import date

import pytest

from risk_monitor.dashboard_data import (
    load_dashboard_data,
    load_drawdowns,
    load_forecasts,
    load_freshness,
    load_prices,
    load_returns,
    load_rolling_volatility,
    load_scores,
)


def test_symbol_aware_loaders_filter_consistently() -> None:
    assert set(load_prices(symbol="SPY")["symbol"]) == {"SPY"}
    assert set(load_returns(symbol="QQQ")["symbol"]) == {"QQQ"}
    assert set(load_rolling_volatility(symbol="SPY")["symbol"]) == {"SPY"}
    assert set(load_drawdowns(symbol="QQQ")["symbol"]) == {"QQQ"}
    assert set(load_forecasts(symbol="SPY")["symbol"]) == {"SPY"}
    assert set(load_scores(symbol="SPY")["symbol"]) == {"SPY", "ALL"}


def test_freshness_marks_current_dataset_as_historical_example() -> None:
    freshness = load_freshness(symbol="SPY", as_of=date(2026, 9, 29))

    assert freshness.latest_available_price_date == date(2025, 12, 31)
    assert freshness.latest_return_date == date(2025, 12, 31)
    assert freshness.model_training_cutoff == date(2025, 12, 31)
    assert freshness.forecast_start_date == date(2026, 1, 2)
    assert freshness.forecast_end_date == date(2026, 1, 8)
    assert freshness.forecast_status == "historical/example"
    assert freshness.is_current is False


def test_dashboard_data_contains_selected_symbol_and_derived_fields() -> None:
    data = load_dashboard_data("QQQ", as_of=date(2026, 9, 29))

    assert data.selected_symbol == "QQQ"
    assert {"volatility_20d", "volatility_50d"}.issubset(data.rolling_volatility.columns)
    assert "drawdown_pct" in data.drawdowns.columns
    assert data.freshness.selected_symbol == "QQQ"


def test_loaders_reject_unknown_symbols() -> None:
    with pytest.raises(ValueError, match="Unknown symbol"):
        load_dashboard_data("DIA")
