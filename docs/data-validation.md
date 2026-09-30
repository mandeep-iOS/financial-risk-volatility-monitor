# Data Validation Notes

Phase 2 Step 2 validated the raw Nasdaq OHLCV files fetched for `SPY` and `QQQ`.

## Scope

- Files checked:
  - `data/raw/spy_daily_nasdaq.csv`
  - `data/raw/qqq_daily_nasdaq.csv`
- Calendar used for expected sessions: NYSE.
- Date range validated: `2016-09-28` through `2025-12-31`.

## Checks

- Required schema: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.
- Chronological date order.
- Duplicate dates.
- Missing required values.
- Nonpositive OHLCV values.
- OHLC internal consistency.
- Missing and unexpected trading sessions relative to the NYSE calendar.

## Results

Both files passed all Step 2 checks.

| Symbol | Rows | First date | Last date | Missing sessions | Unexpected sessions | Status |
| --- | ---: | --- | --- | ---: | ---: | --- |
| `SPY` | 2,328 | 2016-09-28 | 2025-12-31 | 0 | 0 | pass |
| `QQQ` | 2,328 | 2016-09-28 | 2025-12-31 | 0 | 0 | pass |

The full machine-readable report is stored at `data/metadata/price_validation_report.json`.

## Limitation

This step validates structure, ordering, missingness, positivity, OHLC consistency, and calendar coverage. It does not yet resolve adjusted-versus-unadjusted price behavior, holidays/corporate actions narrative, or return calculations; those are handled in later Phase 2 steps.

