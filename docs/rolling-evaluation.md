# Rolling-Origin Evaluation

Phase 3 Step 4 creates one aligned forecast row for every symbol and test target
date. The test period is 2024-02-23 through 2025-12-31.

For target date `t`, both models use only returns dated before `t`:

- The historical baseline uses the previous 20 returns.
- GARCH(1,1) is refit on an expanding window at every target date.
- The realized variance proxy is `ReturnPct_t ** 2`, in percentage-points-squared.

The output is `data/metadata/rolling_forecasts.csv`, with forecast origin,
realized proxy, baseline variance, and GARCH variance columns. This step prepares
aligned forecasts; MAE and QLIKE scoring belong to Phase 3 Step 5.

Run the evaluation with:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/run_evaluation.py
```

Because GARCH is refit for each target date, the full run can take longer than the
earlier static fit. The saved metadata records the expanding-window rule and
realized proxy definition.
