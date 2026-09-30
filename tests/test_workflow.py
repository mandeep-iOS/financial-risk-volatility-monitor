import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_generated_workflow_artifacts_are_aligned_and_positive() -> None:
    forecasts = pd.read_csv(ROOT / "data/metadata/rolling_forecasts.csv", parse_dates=["target_date", "forecast_origin"])
    assert (forecasts["forecast_origin"] < forecasts["target_date"]).all()
    assert (forecasts[["baseline_variance_pct2", "garch_variance_pct2"]] > 0).all().all()
    assert forecasts.groupby("symbol").size().to_dict() == {"QQQ": 466, "SPY": 466}


def test_five_day_artifact_has_two_models_and_five_horizons() -> None:
    payload = json.loads((ROOT / "data/metadata/five_day_forecast.json").read_text(encoding="utf-8"))
    frame = pd.DataFrame(payload["forecasts"])
    assert set(frame["model"]) == {"baseline", "garch"}
    assert frame.groupby(["symbol", "model"])["horizon"].nunique().eq(5).all()
    assert (frame["variance_pct2"] >= 0).all()
    assert (frame["volatility_pct"] >= 0).all()
