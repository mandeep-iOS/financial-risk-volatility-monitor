"""Inspect the historical-variance baseline configuration and first forecasts."""

from risk_monitor.baseline import BASELINE_WINDOW, historical_variance_forecasts
from risk_monitor.volatility import load_returns


def main() -> None:
    forecasts = historical_variance_forecasts(load_returns())
    print(f"window_sessions={BASELINE_WINDOW}")
    print(f"forecast_rows={len(forecasts)}")
    print(forecasts.groupby("symbol").head(2).to_string(index=False))
    print(f"positive_forecasts={forecasts['forecast_variance_pct2'].gt(0).all()}")


if __name__ == "__main__":
    main()
