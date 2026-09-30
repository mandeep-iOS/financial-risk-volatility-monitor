"""Create the five-trading-day variance and volatility forecast."""

from risk_monitor.forecast import forecast_all_symbols


def main() -> None:
    for row in forecast_all_symbols():
        print(row)


if __name__ == "__main__":
    main()
