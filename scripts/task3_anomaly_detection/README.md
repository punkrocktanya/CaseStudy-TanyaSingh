# Task 3: Anomaly detection

Screen unusual cycles using robust trend and local deviations, plus DBSCAN clustering and parameter sensitivity.

## Run

From the project root:

```bash
python scripts/task3_anomaly_detection/task3_anomaly_detection.py
```

Run Tasks 1 and 2 first. Unsupervised noise labels are candidates for review, not confirmed faults.

This entry point runs the validated implementation files in this folder in order and then copies their reviewable results into this folder. It stops on an error. The authoritative working outputs remain in `scripts/outputs/`; copies are refreshed only when this task runs. Intermediate Excel workbooks, cleaned Parquet files and per-row interval diagnostics are omitted from the copies to avoid duplicating large files.

## Implementation

- [07_detect_battery_anomalies.py](07_detect_battery_anomalies.py)

## Results and plots

- [outputs/07_anomaly_detection/](outputs/07_anomaly_detection/)

Additional investigation utility: `investigate_battery_anomalies.py`.
