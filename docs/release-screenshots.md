# Release Screenshot Checklist

Capture screenshots from the React frontend at a consistent 1440 x 900 desktop viewport with the FastAPI service running.

Recommended captures:

1. `overview.png`: `/overview`, SPY selected, hero, KPI grid, chart, insight, and scenario card visible.
2. `compare.png`: `/compare`, full historical range, KPI comparison, normalized growth, and drawdown visible.
3. `forecast.png`: `/forecast`, SPY selected, freshness pills, forecast chart, and interpretation visible.
4. `model-evidence.png`: `/evidence`, evaluation metadata, MAE/QLIKE explanations, both winner cards, and diagnostics disclosure visible.

The browser smoke review for all four screens was completed during Phase D preparation. Local screenshots can be captured with browser screenshot tooling after starting:

```bash
.venv/bin/python scripts/run_api.py
cd frontend && npm run dev
```
