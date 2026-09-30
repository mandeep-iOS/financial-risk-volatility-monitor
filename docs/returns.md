# Return Calculation Notes

Phase 2 Step 4 calculated daily close-to-close percentage returns for `SPY` and `QQQ`.

## Formula

Returns use the raw Nasdaq `Close` field:

```text
ReturnPct_t = 100 * (Close_t / Close_{t-1} - 1)
```

Units are **percent**, not decimal returns.

## Inputs and Outputs

| Symbol | Input rows | Output rows | Dropped rows | First return date | Last return date |
| --- | ---: | ---: | ---: | --- | --- |
| `SPY` | 2,328 | 2,327 | 1 | 2016-09-29 | 2025-12-31 |
| `QQQ` | 2,328 | 2,327 | 1 | 2016-09-29 | 2025-12-31 |

The first price row for each symbol is dropped from the return files because it has no prior close for a daily percentage-change calculation.

Processed files:

- `data/processed/spy_daily_returns.csv`
- `data/processed/qqq_daily_returns.csv`

Metadata:

- `data/metadata/return_calculation_metadata.json`

## Adjustment Note

These are close-to-close price returns based on raw Nasdaq `Close` prices. They are not total returns and are not assumed to be dividend-adjusted.

