import pytest

from risk_monitor.dashboard_data import calculate_scenarios, load_dashboard_data, summarize_asset


def test_summarize_asset_returns_selected_symbol_metrics() -> None:
    summary = summarize_asset(load_dashboard_data("SPY"))

    assert summary.latest_close > 0
    assert summary.latest_price_date.isoformat() == "2025-12-31"
    assert summary.volatility_20d_pct > 0
    assert summary.volatility_50d_pct > 0
    assert summary.max_drawdown_pct <= summary.current_drawdown_pct
    assert summary.worst_daily_return_pct < 0


def test_calculate_scenarios_returns_dollar_impacts() -> None:
    scenarios = calculate_scenarios(10_000, latest_return_pct=-0.5, worst_return_pct=-10.0)

    assert scenarios[0].dollar_impact == pytest.approx(100)
    assert scenarios[2].dollar_impact == pytest.approx(-50)
    assert scenarios[-1].label == "Worst daily return in selected data"
