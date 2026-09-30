"""Build the local SQLite store for validated prices and returns."""

from __future__ import annotations

from risk_monitor.storage import build_sqlite_store


def main() -> None:
    result = build_sqlite_store()
    print(f"database={result.database_path}")
    print(f"sha256={result.sha256}")
    for summary in result.symbols:
        print(
            f"{summary.symbol}: prices={summary.price_rows} "
            f"({summary.first_price_date} to {summary.last_price_date}), "
            f"returns={summary.return_rows} "
            f"({summary.first_return_date} to {summary.last_return_date})"
        )


if __name__ == "__main__":
    main()

