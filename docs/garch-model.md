# GARCH(1,1) Fit

The project uses a constant-mean Gaussian GARCH(1,1) specification:

- Mean model: constant
- Volatility model: GARCH with `p=1`, `q=1`
- Innovation distribution: normal
- Input: daily close-to-close returns in percentage points
- Training cutoff: 2024-02-22

The model is fit separately for SPY and QQQ using only returns dated on or before
the cutoff. The fit script records the sample size, dates, parameter estimates,
convergence flag, and log likelihood in
`data/metadata/garch_fit_metadata.json`.

Run the fit with:

```sh
.venv/bin/python scripts/fit_garch.py
```

This step establishes the model configuration and fit. One-day-ahead rolling
forecasts and comparison with the historical baseline are handled in later
steps.
