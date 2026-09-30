import sqlite3
from pathlib import Path

from risk_monitor.plots import create_exploratory_charts, load_table


def make_plot_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE prices (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER NOT NULL
            );
            CREATE TABLE returns (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                close REAL NOT NULL,
                return_pct REAL NOT NULL
            );
            """
        )
        connection.executemany(
            "INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("SPY", "2025-01-02", 100, 101, 99, 100, 1000),
                ("SPY", "2025-01-03", 101, 102, 100, 101, 1100),
                ("QQQ", "2025-01-02", 200, 201, 199, 200, 2000),
                ("QQQ", "2025-01-03", 202, 203, 201, 202, 2100),
            ],
        )
        connection.executemany(
            "INSERT INTO returns VALUES (?, ?, ?, ?)",
            [
                ("SPY", "2025-01-03", 101, 1.0),
                ("QQQ", "2025-01-03", 202, 1.0),
            ],
        )


def test_load_table_sorts_symbol_and_date(tmp_path: Path) -> None:
    database_path = tmp_path / "plot.sqlite"
    make_plot_database(database_path)

    prices = load_table(database_path, "prices")

    assert prices.loc[0, "symbol"] == "QQQ"
    assert prices.loc[0, "date"].strftime("%Y-%m-%d") == "2025-01-02"


def test_create_exploratory_charts_writes_pngs_and_metadata(tmp_path: Path) -> None:
    database_path = tmp_path / "plot.sqlite"
    figures_dir = tmp_path / "figures"
    metadata_dir = tmp_path / "metadata"
    make_plot_database(database_path)

    results = create_exploratory_charts(
        database_path=database_path,
        figures_dir=figures_dir,
        metadata_dir=metadata_dir,
    )

    assert len(results) == 3
    assert (figures_dir / "daily_close_prices.png").stat().st_size > 0
    assert (figures_dir / "daily_returns.png").stat().st_size > 0
    assert (figures_dir / "return_distributions.png").stat().st_size > 0
    assert (metadata_dir / "exploratory_figures_metadata.json").exists()

