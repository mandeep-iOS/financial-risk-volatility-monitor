import pandas as pd
import pytest

from risk_monitor.features import RETURN_COLUMN, calculate_returns_frame


def test_calculate_returns_frame_uses_percent_units_and_drops_first_row() -> None:
    prices = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"]),
            "Close": [100.0, 105.0, 102.9],
        }
    )

    returns = calculate_returns_frame(prices)

    assert list(returns["Date"].dt.strftime("%Y-%m-%d")) == ["2025-01-03", "2025-01-06"]
    assert len(returns) == len(prices) - 1
    assert returns[RETURN_COLUMN].round(6).tolist() == [5.0, -2.0]


def test_calculate_returns_frame_sorts_dates_before_calculation() -> None:
    prices = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2025-01-03", "2025-01-02"]),
            "Close": [105.0, 100.0],
        }
    )

    returns = calculate_returns_frame(prices)

    assert returns.loc[0, "Date"].strftime("%Y-%m-%d") == "2025-01-03"
    assert returns.loc[0, RETURN_COLUMN] == pytest.approx(5.0)
