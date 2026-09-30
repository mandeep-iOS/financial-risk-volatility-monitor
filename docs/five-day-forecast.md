# Five-Trading-Day Forecast

The forward forecast starts after the latest stored observation, 2025-12-31, and
uses the next five NYSE sessions. The baseline repeats the latest 20-session
sample variance across the horizon. GARCH produces a recursive five-step variance
forecast from the fit through 2025-12-31.

The output contains separate fields for:

- `variance_pct2`: forecast variance in percentage-points-squared
- `volatility_pct`: square root of forecast variance in percentage points

Generate the forecast with:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/forecast_five_days.py
```

The machine-readable result is saved to `data/metadata/five_day_forecast.json`.
It is an educational conditional forecast based on the stored raw-Close return
series, not a prediction of price direction or investment suitability.
