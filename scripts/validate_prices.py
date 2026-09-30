"""Validate raw project price files."""

from __future__ import annotations

from risk_monitor.validation import validate_all_prices


def main() -> None:
    results = validate_all_prices()
    for result in results:
        print(
            f"{result.symbol}: {result.status}, rows={result.row_count}, "
            f"{result.first_date} to {result.last_date}, "
            f"missing_sessions={len(result.missing_sessions)}, "
            f"unexpected_sessions={len(result.unexpected_sessions)}"
        )


if __name__ == "__main__":
    main()

