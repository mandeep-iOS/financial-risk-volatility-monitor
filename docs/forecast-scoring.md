# Forecast Scoring

The aligned rolling forecasts are scored with two metrics:

- MAE: mean absolute error between forecast variance and the next day's squared
  percentage return, in percentage-points-squared.
- QLIKE: `mean(y / forecast - log(y / forecast) - 1)` for rows with strictly
  positive realized and forecast variance.

MAE uses every aligned valid row. QLIKE excludes rows where the realized proxy is
zero because its logarithm is undefined. This exclusion is reported through the
QLIKE sample count; it does not remove rows from MAE.

Run the scoring step after the rolling evaluation:

```sh
.venv/bin/python scripts/score_forecasts.py
```

Results are written to `data/metadata/forecast_scores.json`. Metrics compare the
models' variance forecasts, not volatility forecasts, and the realized proxy is a
noisy one-day measure rather than directly observed integrated variance.
