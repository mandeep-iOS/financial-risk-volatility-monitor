import pandas as pd

from risk_monitor.evaluation import run_rolling_evaluation


def test_evaluation_aligns_models_and_excludes_target_return(monkeypatch) -> None:
    dates = pd.date_range("2020-01-01", periods=110)
    returns = pd.DataFrame(
        {"symbol": ["SPY"] * 110, "date": dates, "return_pct": [0.1] * 109 + [50.0]}
    )

    monkeypatch.setattr(
        "risk_monitor.evaluation.garch_one_step_variance",
        lambda returns, symbol, target_date: 2.0,
    )
    result = run_rolling_evaluation(
        returns, target_start=pd.Timestamp("2020-04-10"), baseline_window=20
    )

    assert result["target_date"].min() == pd.Timestamp("2020-04-10")
    assert (result["forecast_origin"] < result["target_date"]).all()
    assert result.iloc[-1]["realized_variance_proxy_pct2"] == 2500.0
    assert result.iloc[-1]["baseline_variance_pct2"] == 0.0
    assert result["garch_variance_pct2"].eq(2.0).all()
