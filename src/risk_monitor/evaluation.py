"""Leakage-controlled rolling-origin variance forecast evaluation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from risk_monitor.baseline import BASELINE_WINDOW, VARIANCE_COLUMN, historical_variance_forecasts
from risk_monitor.config import DATABASE_PATH, METADATA_DIR
from risk_monitor.garch import fit_garch
from risk_monitor.split import TEST_START_DATE
from risk_monitor.volatility import load_returns


@dataclass(frozen=True)
class EvaluationSummary:
    """Metadata for one rolling-origin evaluation run."""

    database_path: str
    test_start_date: str
    test_end_date: str
    symbols: list[str]
    target_rows: int
    baseline_window: int
    garch_refit: str
    realized_proxy: str


def garch_one_step_variance(returns: pd.DataFrame, symbol: str, target_date: pd.Timestamp) -> float:
    """Fit through the forecast origin and return the next target variance."""

    history = returns[(returns["symbol"] == symbol) & (returns["date"] < target_date)]
    result, _ = fit_garch(history, symbol=symbol, training_end=history["date"].max())
    forecast = result.forecast(horizon=1, reindex=False).variance.iloc[-1, 0]
    return float(forecast)


def run_rolling_evaluation(
    returns: pd.DataFrame,
    *,
    target_start: pd.Timestamp = TEST_START_DATE,
    baseline_window: int = BASELINE_WINDOW,
) -> pd.DataFrame:
    """Create aligned baseline and expanding-window GARCH target forecasts."""

    ordered = returns.sort_values(["symbol", "date"]).copy()
    targets = ordered[ordered["date"] >= target_start][["symbol", "date", "return_pct"]]
    baseline = historical_variance_forecasts(
        ordered, window=baseline_window, target_start=target_start
    ).rename(columns={VARIANCE_COLUMN: "baseline_variance_pct2"})
    rows: list[dict[str, object]] = []
    for target in targets.itertuples(index=False):
        garch_variance = garch_one_step_variance(ordered, target.symbol, target.date)
        baseline_row = baseline[
            (baseline["symbol"] == target.symbol) & (baseline["date"] == target.date)
        ].iloc[0]
        rows.append(
            {
                "symbol": target.symbol,
                "target_date": target.date,
                "forecast_origin": ordered[
                    (ordered["symbol"] == target.symbol) & (ordered["date"] < target.date)
                ]["date"].max(),
                "realized_variance_proxy_pct2": float(target.return_pct**2),
                "baseline_variance_pct2": float(baseline_row["baseline_variance_pct2"]),
                "garch_variance_pct2": garch_variance,
            }
        )
    return pd.DataFrame(rows)


def evaluate_from_store(
    *,
    database_path: Path = DATABASE_PATH,
    metadata_dir: Path = METADATA_DIR,
    output_path: Path | None = None,
) -> tuple[pd.DataFrame, EvaluationSummary]:
    """Run the full rolling evaluation and write aligned forecast rows."""

    returns = load_returns(database_path)
    forecasts = run_rolling_evaluation(returns)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = metadata_dir / "rolling_forecasts.csv"
    forecasts.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    summary = EvaluationSummary(
        database_path=str(database_path),
        test_start_date=forecasts["target_date"].min().date().isoformat(),
        test_end_date=forecasts["target_date"].max().date().isoformat(),
        symbols=sorted(forecasts["symbol"].unique().tolist()),
        target_rows=len(forecasts),
        baseline_window=BASELINE_WINDOW,
        garch_refit="expanding window at every target date using prior returns",
        realized_proxy="target day's squared daily percentage return",
    )
    (metadata_dir / "rolling_evaluation_metadata.json").write_text(
        json.dumps({"created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"), **asdict(summary)}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return forecasts, summary
