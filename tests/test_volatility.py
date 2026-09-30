from pathlib import Path

import pandas as pd

from risk_monitor.volatility import calculate_rolling_volatility, create_volatility_analysis


def test_calculate_rolling_volatility_is_grouped_and_annualized() -> None:
    returns = pd.DataFrame(
        {
            "symbol": ["SPY"] * 4 + ["QQQ"] * 4,
            "date": pd.date_range("2025-01-01", periods=4).tolist() * 2,
            "return_pct": [1.0, 2.0, 3.0, 4.0, 2.0, 2.0, 4.0, 4.0],
        }
    )

    result = calculate_rolling_volatility(returns, windows=(2,))

    expected = ((0.5**2 + 0.5**2) ** 0.5) * (252**0.5)
    assert pd.isna(result.loc[0, "volatility_2d"])
    assert result.loc[1, "volatility_2d"] == expected
    assert result.loc[5, "volatility_2d"] == 0.0


def test_create_volatility_analysis_writes_figures(tmp_path: Path) -> None:
    database_path = tmp_path / "plot.sqlite"
    figures_dir = tmp_path / "figures"
    metadata_dir = tmp_path / "metadata"
    import sqlite3

    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE returns (symbol TEXT, date TEXT, return_pct REAL)")
        rows = [(symbol, f"2025-01-{day:02d}", float(day % 5 - 2)) for symbol in ("SPY", "QQQ") for day in range(1, 31)]
        connection.executemany("INSERT INTO returns VALUES (?, ?, ?)", rows)

    results = create_volatility_analysis(
        database_path=database_path, figures_dir=figures_dir, metadata_dir=metadata_dir
    )

    assert len(results) == 2
    assert (figures_dir / "rolling_volatility.png").stat().st_size > 0
    assert (figures_dir / "squared_return_acf_pacf.png").stat().st_size > 0
    assert (metadata_dir / "volatility_analysis_metadata.json").exists()
