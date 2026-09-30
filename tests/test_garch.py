import pandas as pd

from risk_monitor.garch import fit_garch


def test_fit_garch_uses_only_data_through_cutoff() -> None:
    dates = pd.date_range("2020-01-01", periods=180)
    returns = pd.DataFrame(
        {
            "symbol": ["SPY"] * 180,
            "date": dates,
            "return_pct": [0.1 if index % 2 else -0.1 for index in range(180)],
        }
    )

    result, training = fit_garch(
        returns, symbol="SPY", training_end=pd.Timestamp("2020-05-29")
    )

    assert len(training) == 150
    assert result.model.volatility.p == 1
    assert result.model.volatility.q == 1
    assert result.model.distribution.name == "Normal"
