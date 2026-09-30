import sqlite3
from pathlib import Path

import pandas as pd

from risk_monitor.storage import build_sqlite_store


def write_price_csv(path: Path, close_values: list[float]) -> None:
    dates = pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"])
    pd.DataFrame(
        {
            "Date": dates,
            "Open": close_values,
            "High": [value + 1 for value in close_values],
            "Low": [value - 1 for value in close_values],
            "Close": close_values,
            "Volume": [1000, 1100, 1200],
        }
    ).to_csv(path, index=False)


def write_return_csv(path: Path, close_values: list[float]) -> None:
    dates = pd.to_datetime(["2025-01-03", "2025-01-06"])
    returns = [
        100 * (close_values[1] / close_values[0] - 1),
        100 * (close_values[2] / close_values[1] - 1),
    ]
    pd.DataFrame(
        {
            "Date": dates,
            "Close": close_values[1:],
            "ReturnPct": returns,
        }
    ).to_csv(path, index=False)


def test_build_sqlite_store_writes_expected_tables(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    metadata_dir = tmp_path / "metadata"
    raw_dir.mkdir()
    processed_dir.mkdir()

    write_price_csv(raw_dir / "spy_daily_nasdaq.csv", [100.0, 101.0, 102.0])
    write_price_csv(raw_dir / "qqq_daily_nasdaq.csv", [200.0, 202.0, 204.0])
    write_return_csv(processed_dir / "spy_daily_returns.csv", [100.0, 101.0, 102.0])
    write_return_csv(processed_dir / "qqq_daily_returns.csv", [200.0, 202.0, 204.0])

    database_path = tmp_path / "risk_monitor.sqlite"
    result = build_sqlite_store(
        database_path=database_path,
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        metadata_dir=metadata_dir,
    )

    assert database_path.exists()
    assert result.sha256
    assert (metadata_dir / "sqlite_store_metadata.json").exists()

    with sqlite3.connect(database_path) as connection:
        price_rows = connection.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
        return_rows = connection.execute("SELECT COUNT(*) FROM returns").fetchone()[0]
        provenance_rows = connection.execute("SELECT COUNT(*) FROM provenance").fetchone()[0]
        symbols = connection.execute(
            "SELECT DISTINCT symbol FROM prices ORDER BY symbol"
        ).fetchall()

    assert price_rows == 6
    assert return_rows == 4
    assert provenance_rows > 0
    assert symbols == [("QQQ",), ("SPY",)]

