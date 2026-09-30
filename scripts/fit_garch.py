"""Fit and record the Phase 3 GARCH(1,1) models."""

from risk_monitor.garch import fit_all_garch


def main() -> None:
    for summary in fit_all_garch():
        print(
            f"{summary.symbol}: rows={summary.training_rows}, "
            f"cutoff={summary.training_end_date}, convergence={summary.convergence_flag}, "
            f"parameters={summary.parameters}"
        )


if __name__ == "__main__":
    main()
