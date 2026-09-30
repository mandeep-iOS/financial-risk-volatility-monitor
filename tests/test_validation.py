from pathlib import Path

import pandas as pd

from risk_monitor.validation import validate_price_file


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def test_validate_price_file_passes_clean_sample(tmp_path: Path) -> None:
    path = tmp_path / "clean.csv"
    write_csv(
        path,
        [
            {
                "Date": "2025-01-02",
                "Open": 100,
                "High": 101,
                "Low": 99,
                "Close": 100.5,
                "Volume": 1000,
            },
            {
                "Date": "2025-01-03",
                "Open": 101,
                "High": 102,
                "Low": 100,
                "Close": 101.5,
                "Volume": 1100,
            },
        ],
    )

    result = validate_price_file("TEST", path)

    assert result.status == "pass"
    assert result.row_count == 2
    assert result.missing_sessions == []
    assert result.unexpected_sessions == []


def test_validate_price_file_reports_quality_issues(tmp_path: Path) -> None:
    path = tmp_path / "dirty.csv"
    write_csv(
        path,
        [
            {
                "Date": "2025-01-06",
                "Open": 100,
                "High": 99,
                "Low": 98,
                "Close": 100.5,
                "Volume": 1000,
            },
            {
                "Date": "2025-01-02",
                "Open": 101,
                "High": 102,
                "Low": 100,
                "Close": 101.5,
                "Volume": 1100,
            },
            {
                "Date": "2025-01-02",
                "Open": -101,
                "High": 102,
                "Low": 100,
                "Close": 101.5,
                "Volume": 1100,
            },
        ],
    )

    result = validate_price_file("TEST", path)

    assert result.status == "fail"
    assert result.duplicate_dates == ["2025-01-02"]
    assert result.non_chronological_dates is True
    assert result.nonpositive_values["Open"] == 1
    assert result.invalid_ohlc_rows == 2
    assert "2025-01-03" in result.missing_sessions

