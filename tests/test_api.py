from fastapi.testclient import TestClient

from risk_monitor.api import app

client = TestClient(app)


def test_health_and_symbols() -> None:
    assert client.get("/health").json()["status"] == "ok"
    symbols = client.get("/symbols")
    assert symbols.status_code == 200
    assert {item["symbol"] for item in symbols.json()} == {"SPY", "QQQ"}


def test_compare_returns_available_bounds_and_accepts_range() -> None:
    response = client.get("/compare", params={"start_date": "2020-01-01", "end_date": "2022-12-31"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["available_start_date"] == "2016-09-28"
    assert payload["available_end_date"] == "2025-12-31"
    assert payload["start_date"] == "2020-01-02"


def test_compare_rejects_invalid_or_empty_ranges() -> None:
    reversed_range = client.get("/compare", params={"start_date": "2025-01-01", "end_date": "2020-01-01"})
    empty_range = client.get("/compare", params={"start_date": "2006-01-01", "end_date": "2015-12-31"})
    assert reversed_range.status_code == 400
    assert "on or before" in reversed_range.json()["detail"]
    assert empty_range.status_code == 400
    assert empty_range.json()["detail"] == (
        "No data available for selected range. Available range is 2016-09-28 to 2025-12-31."
    )


def test_forecast_validates_and_returns_units(monkeypatch) -> None:
    class Row:
        forecast_date = "2026-01-02"
        horizon = 1
        model = "baseline"
        variance_pct2 = 1.0
        volatility_pct = 1.0
        training_end_date = "2025-12-31"

    monkeypatch.setattr("risk_monitor.api.load_returns", lambda path: object())
    monkeypatch.setattr("risk_monitor.api.create_five_day_forecast", lambda returns, symbol, horizon: [Row()])

    response = client.post("/forecast", json={"symbol": "spy", "horizon": 1})

    assert response.status_code == 200
    assert response.json()["symbol"] == "SPY"
    assert response.json()["variance_units"] == "percentage-points-squared"
    assert response.json()["forecasts"][0]["model"] == "baseline"


def test_forecast_rejects_unknown_symbol() -> None:
    response = client.post("/forecast", json={"symbol": "DIA", "horizon": 1})

    assert response.status_code == 404


def test_forecast_rejects_horizon_over_five() -> None:
    response = client.post("/forecast", json={"symbol": "SPY", "horizon": 6})

    assert response.status_code == 422
