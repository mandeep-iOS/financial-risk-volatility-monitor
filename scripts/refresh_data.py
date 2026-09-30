"""Refresh local data and regenerate derived exploratory artifacts."""

from risk_monitor.data_fetch import fetch_all_assets
from risk_monitor.features import calculate_all_returns
from risk_monitor.plots import create_exploratory_charts
from risk_monitor.storage import build_sqlite_store
from risk_monitor.validation import validate_all_prices
from risk_monitor.volatility import create_volatility_analysis


def main() -> None:
    fetch_all_assets()
    validate_all_prices()
    calculate_all_returns()
    build_sqlite_store()
    create_exploratory_charts()
    create_volatility_analysis()
    print("Raw data and derived exploratory artifacts refreshed.")
    print("Regenerate models and forecast artifacts with their dedicated scripts.")


if __name__ == "__main__":
    main()
