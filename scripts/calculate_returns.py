"""Calculate daily percentage returns from validated raw prices."""

from __future__ import annotations

from risk_monitor.features import calculate_all_returns


def main() -> None:
    results = calculate_all_returns()
    for result in results:
        print(
            f"{result.symbol}: {result.output_rows} returns, "
            f"{result.first_return_date} to {result.last_return_date}, "
            f"dropped_rows={result.dropped_rows}, units={result.return_units}"
        )


if __name__ == "__main__":
    main()

