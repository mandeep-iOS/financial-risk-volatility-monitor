from risk_monitor.data_fetch import build_nasdaq_url, normalize_nasdaq_rows, rows_to_csv


def test_build_nasdaq_url_contains_symbol_and_dates() -> None:
    url = build_nasdaq_url("SPY", "2015-01-02", "2025-12-31")

    assert "quote/SPY/historical" in url
    assert "assetclass=etf" in url
    assert "fromdate=2015-01-02" in url
    assert "todate=2025-12-31" in url


def test_normalize_nasdaq_rows_sorts_and_cleans_values() -> None:
    payload = {
        "data": {
            "tradesTable": {
                "rows": [
                    {
                        "date": "01/03/2025",
                        "open": "$102.00",
                        "high": "103.50",
                        "low": "101.25",
                        "close": "$102.75",
                        "volume": "1,234,500",
                    },
                    {
                        "date": "01/02/2025",
                        "open": "100.00",
                        "high": "101.00",
                        "low": "99.50",
                        "close": "100.50",
                        "volume": "987,600",
                    },
                ]
            }
        }
    }

    rows = normalize_nasdaq_rows(payload)
    csv_text = rows_to_csv(rows)

    assert rows[0]["Date"] == "2025-01-02"
    assert rows[1]["Date"] == "2025-01-03"
    assert rows[1]["Close"] == "102.75"
    assert rows[1]["Volume"] == "1234500"
    assert csv_text.splitlines()[0] == "Date,Open,High,Low,Close,Volume"

