"""Run the chronological rolling-origin forecast evaluation."""

from risk_monitor.evaluation import evaluate_from_store


def main() -> None:
    _, summary = evaluate_from_store()
    print(summary)


if __name__ == "__main__":
    main()
