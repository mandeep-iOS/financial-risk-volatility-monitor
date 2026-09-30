# Chronological Backtesting Split

Phase 3 modeling uses a fixed split chosen before forecast scoring:

| Partition | Dates | Rows per symbol |
| --- | --- | ---: |
| Training history | 2016-09-29 through 2024-02-22 | 1,861 |
| Test targets | 2024-02-23 through 2025-12-31 | 466 |

The first test target is 2024-02-23. Its forecast origin may use observations
through 2024-02-22 and must not use the target return. Every later target follows
the same rule: a forecast for date `t` is formed using data dated before `t`.

The baseline and GARCH forecasts will use the same symbols, target dates, return
units, and next-day squared-return realized-variance proxy. The shared scoring
sample will include only dates where both forecasts and the realized proxy are
valid. No test-period tuning or removal of difficult market periods is allowed.

Run the audit command from the project root:

```sh
.venv/bin/python scripts/inspect_split.py
```

The split is a modeling contract. Baseline window selection and GARCH fitting are
reserved for the following Phase 3 steps.
