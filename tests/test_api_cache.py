from risk_monitor.api import cached_forecast


def test_cached_forecast_exposes_reuse_contract() -> None:
    cached_forecast.cache_clear()
    assert cached_forecast.cache_info().maxsize == 4
