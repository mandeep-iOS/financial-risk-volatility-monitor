# Validated Data Store

Phase 2 Step 5 stores validated prices and calculated returns in a local SQLite database.

## Artifact

- Database: `data/processed/risk_monitor.sqlite`
- Metadata: `data/metadata/sqlite_store_metadata.json`
- Database checksum: recorded in `sqlite_store_metadata.json`

## Tables

| Table | Description | Rows |
| --- | --- | ---: |
| `prices` | Validated daily OHLCV rows keyed by symbol and date | 4,656 |
| `returns` | Daily close-to-close percentage returns keyed by symbol and date | 4,654 |
| `provenance` | Source paths, source checksums, units, and adjustment notes | 12 |

## Symbol Coverage

| Symbol | Price rows | Price range | Return rows | Return range |
| --- | ---: | --- | ---: | --- |
| `SPY` | 2,328 | 2016-09-28 to 2025-12-31 | 2,327 | 2016-09-29 to 2025-12-31 |
| `QQQ` | 2,328 | 2016-09-28 to 2025-12-31 | 2,327 | 2016-09-29 to 2025-12-31 |

## Rebuild Command

```bash
.venv/bin/python scripts/build_store.py
```

The command rebuilds the SQLite database from the current raw price CSVs and processed return CSVs.

## Notes

- The raw and processed CSV files remain on disk for transparency.
- The SQLite store is the stable local source for later analysis, charts, modeling, API, and dashboard work.
- Returns are in percent and are based on raw Nasdaq `Close` prices, not total-return or dividend-adjusted prices.

