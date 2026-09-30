# Adjustments, Calendar, and Corporate Actions

Phase 2 Step 3 documents how the fetched raw price data should be interpreted before return calculation.

## Source Fields

The project currently uses Nasdaq historical quote API responses for `SPY` and `QQQ`, normalized into:

- `Date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

The fetched Nasdaq responses did not include an adjusted-close field. Version 1 will therefore treat the raw `Close` field as a regular close/last price series, not a dividend-adjusted total-return series.

## Adjusted Versus Unadjusted Prices

Working assumption for version 1:

- `Open`, `High`, `Low`, and `Close` are raw historical OHLC prices from Nasdaq's quote API.
- `Close` is suitable for daily close-to-close price-return calculations.
- `Close` is not assumed to include dividend or capital-gain distribution adjustments.
- The project will not describe the return series as total return.

Modeling implication:

- Daily returns in the next step will be price returns based on `Close`.
- ETF distributions may create ex-dividend price drops that appear in close-to-close returns.
- This is acceptable for a version 1 volatility monitor, but it must be disclosed in charts, model evaluation, README, and the case study.

## Market Holidays and Sessions

The validation step used the NYSE calendar from `pandas-market-calendars`.

Measured validation result:

| Symbol | Returned range | Rows | Expected sessions | Missing sessions | Unexpected sessions |
| --- | --- | ---: | ---: | ---: | ---: |
| `SPY` | 2016-09-28 to 2025-12-31 | 2,328 | 2,328 | 0 | 0 |
| `QQQ` | 2016-09-28 to 2025-12-31 | 2,328 | 2,328 | 0 | 0 |

Interpretation:

- Weekends and U.S. market holidays are not rows in the raw files.
- Early-close days are treated as valid trading sessions because daily OHLCV rows are present.
- No calendar gaps were found inside the returned range.
- The requested range began at `2015-01-02`, but Nasdaq returned data beginning `2016-09-28`; the project will use the returned range unless a later approved source change extends the history.

## Corporate Actions

`SPY` and `QQQ` are ETFs that can pay cash distributions. These distributions matter because a raw close series does not represent reinvested distributions.

Known implications for this project:

- Dividend and capital-gain distributions can affect close-to-close price returns around ex-dividend dates.
- The raw Nasdaq OHLCV files do not include distribution rows or adjusted-close values.
- Version 1 will not attempt to reconstruct adjusted closes from separate distribution data.
- Any model comparison will be interpreted as volatility forecasting on the observed close-to-close price-return series, not on total returns.

Split handling:

- The fetched raw files contain no explicit split metadata.
- No split-adjustment claim is made from the Nasdaq files alone.
- If a future source provides explicit split-adjusted or dividend-adjusted prices, that source and adjustment method must be documented before replacing the current returns.

## Publication Language

Use this language in public-facing materials until a different data source is approved:

> Prices are daily OHLCV rows fetched from Nasdaq's historical quote endpoint. Returns are close-to-close price returns based on the raw `Close` field. They are not total returns and are not assumed to be dividend-adjusted.

## References Checked

- Nasdaq Data Link documentation describes historical chart/bar-style access for OHLCV data and mentions adjusted previous-close fields in related products, but the fetched quote endpoint response used here did not include an adjusted-close field.
- State Street's SPY product page describes `SPY` as seeking investment results that correspond generally to the price and yield performance of the S&P 500 Index and references distributions.
- Invesco's QQQ product materials reference distributions and the ETF's Nasdaq-100 exposure.
- Yahoo Finance's historical-price page distinguishes `Close` adjusted for splits from `Adj Close` adjusted for dividends and/or capital-gain distributions; this distinction is useful for documenting what the current Nasdaq file does not provide.

