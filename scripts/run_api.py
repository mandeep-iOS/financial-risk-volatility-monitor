"""Run the local FastAPI service."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("risk_monitor.api:app", host="127.0.0.1", port=8000, reload=False)
