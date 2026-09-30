# Data Quality and Exploratory Observations

This log records observations from the Phase 2 data and figures. It describes the
sample and does not claim that the patterns have a causal explanation or that they
will persist.

## Data quality

- The SPY and QQQ raw files each contain 2,328 rows from 2016-09-28 through
  2025-12-31.
- Both files passed the required schema, chronological-order, duplicate-date,
  missing-value, positive-value, OHLC-consistency, and NYSE-session checks.
- Each symbol produces 2,327 close-to-close returns after dropping the first
  undefined return. The return series runs from 2016-09-29 through 2025-12-31.
- No missing or unexpected NYSE sessions were reported by the validation step.

## Measured observations

- The daily return standard deviation is 1.1553% for SPY and 1.4303% for QQQ in
  this sample. These are descriptive sample statistics, not forecasts.
- The largest absolute returns occur during visibly high-volatility periods. The
  largest recorded return is +12.0031% for QQQ on 2025-04-09; the largest
  negative return is -11.9788% for QQQ on 2020-03-16.
- The maximum 20-session annualized rolling volatility is 93.50% for SPY and
  92.32% for QQQ, both on 2020-03-27. The corresponding 50-session values are
  60.57% and 60.72%.
- On 2025-12-31, 20-session annualized volatility is 8.59% for SPY and 13.17%
  for QQQ; 50-session volatility is 11.71% and 17.23%, respectively.
- The squared-return ACF plots show positive short-lag autocorrelation for both
  symbols, with a gradual decline across the displayed lags. This is consistent
  with volatility clustering in the observed sample and motivates the later
  variance-model comparison.

## Interpretation limits

The plots use raw Close prices, so the returns are not dividend-adjusted total
returns. The squared return is only a noisy proxy for one day's realized
variance. Rolling volatility and ACF/PACF are exploratory diagnostics; they do
not establish causality, investment suitability, or superior forecast performance.
The next phase must use chronological forecast origins and evaluate both models
on identical dates.

## Reproduction

Regenerate the figures with:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/create_charts.py
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/analyze_volatility.py
```

The machine-readable inputs are `data/metadata/price_validation_report.json`,
`data/metadata/return_calculation_metadata.json`, and
`data/metadata/volatility_analysis_metadata.json`.
