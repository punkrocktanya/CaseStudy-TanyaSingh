# Task 6: Reporting and visualization

Produce the capacity prediction, coulombic efficiency, anomaly cluster and RUL figures and the five-page technical report.

## Run

From the project root:

```bash
python scripts/task6_reporting/task6_report_and_visualizations.py
```

Run Tasks 1–5 first. The LSTM seed spread is not a calibrated fleet RUL distribution.

This entry point runs the implementation files in this folder in order and stops on an error. Its authoritative results, plots and intermediate files are written directly to this folder’s `outputs/`. Some large preprocessing intermediates are kept locally and excluded from Git.

## Implementation

- [14_build_task6_visualizations.py](14_build_task6_visualizations.py)
- [build_six_task_report.py](build_six_task_report.py)

## Results and plots

- [outputs/14_reporting_visualization/](outputs/14_reporting_visualization/)
- [outputs/15_consistency_validation/](outputs/15_consistency_validation/) — historical consistency audit
- [Five-page technical report](outputs/Technical_Report.pdf)

`build_battery_report.py`, `build_limitations_report.py` and `build_short_report.py` are historical report builders. The current report uses `build_six_task_report.py`.
