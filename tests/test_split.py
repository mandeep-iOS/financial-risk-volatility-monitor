import pandas as pd
import pytest

from risk_monitor.split import apply_chronological_split, summarize_split


def test_split_is_strictly_chronological() -> None:
    dates = pd.date_range("2024-02-20", periods=4)
    returns = pd.DataFrame({"symbol": ["SPY"] * 4, "date": dates, "return_pct": [1, 2, 3, 4]})

    train, test = apply_chronological_split(returns)

    assert train["date"].max() < test["date"].min()
    assert summarize_split(returns).test_start_date == "2024-02-23"


def test_split_requires_expected_columns() -> None:
    with pytest.raises(ValueError, match="Missing split columns"):
        apply_chronological_split(pd.DataFrame({"date": []}))
