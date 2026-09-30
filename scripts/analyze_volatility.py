"""Create rolling-volatility and squared-return dependence diagnostics."""

from risk_monitor.volatility import create_volatility_analysis


def main() -> None:
    for result in create_volatility_analysis():
        print(f"{result.name}: {result.path} ({result.first_date} to {result.last_date}, units={result.units})")


if __name__ == "__main__":
    main()
