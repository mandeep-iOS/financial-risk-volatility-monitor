"""Metrics for comparing one-day-ahead variance forecasts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from risk_monitor.config import METADATA_DIR

REALIZED_COLUMN = "realized_variance_proxy_pct2"
MODEL_COLUMNS = {
    "baseline": "baseline_variance_pct2",
    "garch": "garch_variance_pct2",
}


@dataclass(frozen=True)
class ForecastScore:
    """Scores for one model and symbol."""

    symbol: str
    model: str
    mae: float
    mae_rows: int
    qlike: float | None
    qlike_rows: int


def qlike_score(realized: pd.Series, forecast: pd.Series) -> float:
    """Calculate mean QLIKE for strictly positive realized and forecast variance."""

    if len(realized) == 0 or (realized <= 0).any() or (forecast <= 0).any():
        raise ValueError("QLIKE requires positive realized and forecast variances")
    ratio = realized / forecast
    return float((ratio - np.log(ratio) - 1).mean())


def score_forecasts(forecasts: pd.DataFrame) -> list[ForecastScore]:
    """Score baseline and GARCH forecasts by symbol on aligned rows."""

    required = {"symbol", REALIZED_COLUMN, *MODEL_COLUMNS.values()}
    missing = required.difference(forecasts.columns)
    if missing:
        raise ValueError(f"Missing scoring columns: {sorted(missing)}")
    scores: list[ForecastScore] = []
    groups = [(symbol, subset) for symbol, subset in forecasts.groupby("symbol", sort=True)]
    groups.append(("ALL", forecasts))
    for symbol, subset in groups:
        realized = subset[REALIZED_COLUMN].astype(float)
        for model, column in MODEL_COLUMNS.items():
            forecast = subset[column].astype(float)
            valid_mae = realized.notna() & forecast.notna()
            mae = float((realized[valid_mae] - forecast[valid_mae]).abs().mean())
            valid_qlike = valid_mae & (realized > 0) & (forecast > 0)
            qlike = (
                qlike_score(realized[valid_qlike], forecast[valid_qlike])
                if valid_qlike.any()
                else None
            )
            scores.append(
                ForecastScore(
                    symbol=symbol,
                    model=model,
                    mae=mae,
                    mae_rows=int(valid_mae.sum()),
                    qlike=qlike,
                    qlike_rows=int(valid_qlike.sum()),
                )
            )
    return scores


def score_forecasts_file(
    forecasts_path: Path,
    *,
    metadata_dir: Path = METADATA_DIR,
) -> list[ForecastScore]:
    """Score a saved rolling-forecast CSV and write machine-readable results."""

    forecasts = pd.read_csv(forecasts_path, parse_dates=["target_date", "forecast_origin"])
    scores = score_forecasts(forecasts)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "forecasts_path": str(forecasts_path),
        "realized_proxy": REALIZED_COLUMN,
        "qlike_note": "QLIKE excludes rows with zero or nonpositive realized variance proxy.",
        "scores": [asdict(score) for score in scores],
    }
    (metadata_dir / "forecast_scores.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return scores
