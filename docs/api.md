# Local API

Start the service with `.venv/bin/python scripts/run_api.py`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service readiness. |
| GET | `/symbols` | Configured symbols and names. |
| GET | `/overview/{symbol}` | Selected-asset summary, series, freshness, and scenarios. |
| GET | `/compare` | SPY/QQQ aligned comparison data and summaries. |
| POST | `/forecast` | Baseline and GARCH forecast for a symbol and horizon 1-5. |
| GET | `/evidence` | Evaluation metadata and model scores. |
| GET | `/evidence/diagnostics/acf-pacf` | Squared-return ACF/PACF image. |

```bash
curl http://127.0.0.1:8000/overview/SPY
curl 'http://127.0.0.1:8000/compare?start_date=2020-01-01&end_date=2025-12-31'
curl http://127.0.0.1:8000/evidence
curl -X POST http://127.0.0.1:8000/forecast -H 'Content-Type: application/json' -d '{"symbol":"QQQ","horizon":5}'
```

Forecast responses are selected-symbol-only and include freshness metadata. Unsupported symbols return `404`; invalid horizons return `422`; unavailable artifacts return `503`.
