"""Score the aligned rolling variance forecasts."""

from pathlib import Path

from risk_monitor.scoring import score_forecasts_file


def main() -> None:
    for score in score_forecasts_file(Path("data/metadata/rolling_forecasts.csv")):
        print(score)


if __name__ == "__main__":
    main()
