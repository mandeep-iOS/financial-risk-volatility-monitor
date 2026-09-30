from datetime import date

from risk_monitor.dashboard_data import compare_assets


def test_compare_assets_returns_aligned_metrics_and_charts() -> None:
    chart_data, summaries = compare_assets(
        start_date=date(2020, 1, 2), end_date=date(2025, 12, 31)
    )

    assert set(chart_data["symbol"]) == {"SPY", "QQQ"}
    assert {"normalized_growth", "drawdown_pct"}.issubset(chart_data.columns)
    assert {summary.symbol for summary in summaries} == {"SPY", "QQQ"}
    assert all(summary.downside_days > 0 for summary in summaries)
    assert all(summary.max_drawdown_pct <= 0 for summary in summaries)


def test_compare_assets_rejects_reversed_dates() -> None:
    try:
        compare_assets(start_date=date(2025, 1, 1), end_date=date(2024, 1, 1))
    except ValueError as error:
        assert "on or before" in str(error)
    else:
        raise AssertionError("Expected reversed comparison dates to fail")
