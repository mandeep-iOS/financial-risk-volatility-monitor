# Historical-Variance Baseline

The Phase 3 baseline uses a fixed 20-session rolling sample variance of daily
close-to-close percentage returns. For a target date `t`:

```text
forecast_variance_t = sample_variance(ReturnPct[t-20], ..., ReturnPct[t-1])
```

The target return is excluded by shifting the return series before applying the
rolling window. Forecast variance is expressed in percentage-points-squared; its
square root would be volatility in percentage points. The 20-session window is
fixed before model comparison and is not tuned on the test period.

The baseline begins producing valid forecasts for the fixed test period beginning
2024-02-23. It will be compared with GARCH on identical target dates in later
steps. This baseline is a transparent reference, not a claim that variance is
constant or that the method is suitable for investment decisions.

Inspect the generated test-period forecast rows with:

```sh
.venv/bin/python scripts/inspect_baseline.py
```
