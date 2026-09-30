"""Fetch raw daily price data for the project assets."""

from __future__ import annotations

from risk_monitor.data_fetch import fetch_all_assets


def main() -> None:
    results = fetch_all_assets()
    for result in results:
        print(
            f"{result.symbol}: {result.row_count} rows, "
            f"{result.first_date} to {result.last_date}, "
            f"sha256={result.sha256}"
        )


if __name__ == "__main__":
    main()

