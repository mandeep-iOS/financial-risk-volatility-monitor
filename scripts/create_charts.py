"""Create exploratory price, return, and distribution charts."""

from __future__ import annotations

from risk_monitor.plots import create_exploratory_charts


def main() -> None:
    results = create_exploratory_charts()
    for result in results:
        print(
            f"{result.name}: {result.path} "
            f"({result.first_date} to {result.last_date}, units={result.units})"
        )


if __name__ == "__main__":
    main()

