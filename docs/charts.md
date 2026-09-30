# Exploratory Charts

From the project root, regenerate the figures from the existing SQLite store:

```sh
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python scripts/create_charts.py
```

The script reads `data/processed/risk_monitor.sqlite` in read-only mode and writes
three PNGs to `docs/figures/`, plus a manifest at
`data/metadata/exploratory_figures_metadata.json`.

| Figure | Content | Period |
| --- | --- | --- |
| [Prices](figures/daily_close_prices.png) | SPY and QQQ raw close prices in USD | 2016-09-28 to 2025-12-31 |
| [Returns](figures/daily_returns.png) | Daily percentage returns in separate panels with shared scales | 2016-09-29 to 2025-12-31 |
| [Distributions](figures/return_distributions.png) | Density histograms using 80 shared bins spanning all returns | 2016-09-29 to 2025-12-31 |

Each symbol contributes 2,328 prices and 2,327 returns. Titles show the observed
date ranges, legends identify symbols, and footnotes identify Nasdaq as the source.
Histogram density is per percentage point; each symbol's histogram integrates to
one. All observations, including extreme returns, are included.

Prices use raw Close and returns are `100 * (Close_t / Close_(t-1) - 1)`.
They are not dividend-adjusted or total returns. Absolute ETF price levels do not
measure comparative investment performance. These plots are descriptive and do
not establish causes or model performance. Rolling volatility and ACF/PACF belong
to the next step.
