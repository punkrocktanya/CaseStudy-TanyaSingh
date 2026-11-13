# Task 6: Reporting and visualization

Produce the capacity prediction, coulombic efficiency, anomaly cluster and RUL figures and the five-page technical report.

## Run

From the project root:

```bash
python scripts/task6_reporting/task6_report_and_visualizations.py
```

Run Tasks 1–5 first. The LSTM seed spread is not a calibrated fleet RUL distribution.

This entry point runs the validated pipeline stages below in order and then copies their reviewable results into this folder. It stops on an error. The authoritative working outputs remain in `scripts/outputs/`; copies are refreshed only when this task runs. Intermediate Excel workbooks, cleaned Parquet files and per-row interval diagnostics are omitted from the copies to avoid duplicating large files.

## Implementation

- [14_build_task6_visualizations.py](../14_build_task6_visualizations.py)
- [build_six_task_report.py](../build_six_task_report.py)

## Results and plots

- [outputs/14_reporting_visualization/](outputs/14_reporting_visualization/)
- [Five-page technical report](outputs/Technical_Report.pdf)
