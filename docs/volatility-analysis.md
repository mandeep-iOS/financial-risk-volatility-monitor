# Rolling Volatility and Dependence Diagnostics

Regenerate the Phase 2 Step 7 outputs from the stored returns with:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/analyze_volatility.py
```

The analysis uses close-to-close returns expressed in percentage points. Rolling
volatility is the sample standard deviation over the trailing 20 or 50 trading
sessions, annualized as `rolling_std * sqrt(252)`. It is labeled as annualized
volatility in percent; it is not forecast variance.

The squared-return diagnostics use `(ReturnPct ** 2)` for each symbol. ACF and
PACF are shown for lags 0 through 20 with approximate 95% confidence bands.
These diagnostics describe serial dependence in the observed sample and do not
prove a particular volatility model is correct. The figures retain the raw
Close return limitation documented in [adjustments and calendar](adjustments-and-calendar.md).

Outputs:

- [Annualized rolling volatility](figures/rolling_volatility.png)
- [Squared-return ACF and PACF](figures/squared_return_acf_pacf.png)
- [Analysis metadata](../data/metadata/volatility_analysis_metadata.json)
