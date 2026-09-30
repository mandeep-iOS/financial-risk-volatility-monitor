import pandas as pd
import pytest

from risk_monitor.scoring import qlike_score, score_forecasts


def test_qlike_requires_positive_realized_variance() -> None:
    with pytest.raises(ValueError, match="positive"):
        qlike_score(pd.Series([0.0]), pd.Series([1.0]))


def test_score_forecasts_reports_mae_and_qlike_sample_sizes() -> None:
    forecasts = pd.DataFrame(
        {
            "symbol": ["SPY"] * 3,
            "realized_variance_proxy_pct2": [1.0, 0.0, 4.0],
            "baseline_variance_pct2": [2.0, 2.0, 2.0],
            "garch_variance_pct2": [1.0, 1.0, 4.0],
        }
    )

    scores = score_forecasts(forecasts)

    baseline, garch = [score for score in scores if score.symbol == "SPY"]
    assert baseline.mae == pytest.approx(5 / 3)
    assert baseline.mae_rows == 3
    assert baseline.qlike_rows == 2
    assert garch.mae == pytest.approx(1 / 3)
    assert garch.qlike == pytest.approx(0.0)
