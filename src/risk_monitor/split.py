"""Chronological train/test contract for variance forecasting."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

TRAIN_END_DATE = pd.Timestamp("2024-02-22")
TEST_START_DATE = pd.Timestamp("2024-02-23")


@dataclass(frozen=True)
class SplitSummary:
    """Fixed chronological split and forecast-origin rules."""

    train_end_date: str
    test_start_date: str
    test_end_date: str
    train_rows_by_symbol: dict[str, int]
    test_rows_by_symbol: dict[str, int]


def apply_chronological_split(returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split returns so test targets occur strictly after the training cutoff."""

    required = {"symbol", "date", "return_pct"}
    missing = required.difference(returns.columns)
    if missing:
        raise ValueError(f"Missing split columns: {sorted(missing)}")
    ordered = returns.sort_values(["symbol", "date"]).copy()
    train = ordered[ordered["date"] <= TRAIN_END_DATE].reset_index(drop=True)
    test = ordered[ordered["date"] >= TEST_START_DATE].reset_index(drop=True)
    if train.empty or test.empty or train["date"].max() >= test["date"].min():
        raise ValueError("Chronological split must have non-overlapping train and test dates")
    return train, test


def summarize_split(returns: pd.DataFrame) -> SplitSummary:
    """Return auditable counts and dates for the fixed split."""

    train, test = apply_chronological_split(returns)
    return SplitSummary(
        train_end_date=TRAIN_END_DATE.date().isoformat(),
        test_start_date=TEST_START_DATE.date().isoformat(),
        test_end_date=test["date"].max().date().isoformat(),
        train_rows_by_symbol=train.groupby("symbol").size().astype(int).to_dict(),
        test_rows_by_symbol=test.groupby("symbol").size().astype(int).to_dict(),
    )
