"""GARCH(1,1) fitting utilities for the volatility monitor."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from arch import arch_model

from risk_monitor.config import DATABASE_PATH, METADATA_DIR
from risk_monitor.split import TRAIN_END_DATE
from risk_monitor.volatility import load_returns

GARCH_P = 1
GARCH_Q = 1
GARCH_MEAN = "Constant"
GARCH_VOLATILITY = "GARCH"
GARCH_DISTRIBUTION = "normal"


@dataclass(frozen=True)
class GarchFitSummary:
    """Auditable summary of one fitted GARCH model."""

    symbol: str
    training_start_date: str
    training_end_date: str
    training_rows: int
    mean: str
    volatility: str
    p: int
    q: int
    distribution: str
    parameters: dict[str, float]
    convergence_flag: int
    loglikelihood: float


def fit_garch(
    returns: pd.DataFrame,
    *,
    symbol: str,
    training_end: pd.Timestamp = TRAIN_END_DATE,
):
    """Fit a constant-mean Gaussian GARCH(1,1) through a fixed cutoff."""

    subset = returns.loc[
        (returns["symbol"] == symbol) & (returns["date"] <= training_end), "return_pct"
    ].dropna()
    if len(subset) < 100:
        raise ValueError("GARCH training data must contain at least 100 returns")
    model = arch_model(
        subset,
        mean=GARCH_MEAN,
        vol=GARCH_VOLATILITY,
        p=GARCH_P,
        q=GARCH_Q,
        dist=GARCH_DISTRIBUTION,
        rescale=False,
    )
    return model.fit(disp="off"), subset


def summarize_garch_fit(result, subset: pd.Series, symbol: str) -> GarchFitSummary:
    """Convert an arch result into JSON-friendly configuration and parameters."""

    return GarchFitSummary(
        symbol=symbol,
        training_start_date=subset.index[0].date().isoformat()
        if isinstance(subset.index, pd.DatetimeIndex)
        else "2016-09-29",
        training_end_date=subset.index[-1].date().isoformat()
        if isinstance(subset.index, pd.DatetimeIndex)
        else TRAIN_END_DATE.date().isoformat(),
        training_rows=len(subset),
        mean=GARCH_MEAN,
        volatility=GARCH_VOLATILITY,
        p=GARCH_P,
        q=GARCH_Q,
        distribution=GARCH_DISTRIBUTION,
        parameters={key: float(value) for key, value in result.params.items()},
        convergence_flag=int(result.convergence_flag),
        loglikelihood=float(result.loglikelihood),
    )


def fit_all_garch(
    *,
    database_path: Path = DATABASE_PATH,
    metadata_dir: Path = METADATA_DIR,
) -> list[GarchFitSummary]:
    """Fit one GARCH model per configured symbol and write fit metadata."""

    returns = load_returns(database_path)
    summaries = []
    for symbol in sorted(returns["symbol"].unique()):
        result, subset = fit_garch(returns, symbol=symbol)
        # Preserve dates explicitly because arch receives a value series.
        training = returns[(returns["symbol"] == symbol) & (returns["date"] <= TRAIN_END_DATE)]
        dated_subset = subset.copy()
        dated_subset.index = pd.DatetimeIndex(training["date"])
        summaries.append(summarize_garch_fit(result, dated_subset, symbol))

    metadata_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "database_path": str(database_path),
        "training_end_date": TRAIN_END_DATE.date().isoformat(),
        "models": [asdict(summary) for summary in summaries],
    }
    (metadata_dir / "garch_fit_metadata.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return summaries
