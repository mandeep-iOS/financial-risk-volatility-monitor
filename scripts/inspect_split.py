"""Print the fixed chronological train/test split summary."""

from dataclasses import asdict

from risk_monitor.split import summarize_split
from risk_monitor.volatility import load_returns


def main() -> None:
    print(asdict(summarize_split(load_returns())))


if __name__ == "__main__":
    main()
