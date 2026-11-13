# Task 3: Anomaly detection

Screen unusual cycles using robust trend and local deviations, plus DBSCAN clustering and parameter sensitivity.

## Run

From the project root:

```bash
python scripts/task3_anomaly_detection/task3_anomaly_detection.py
```

Run Tasks 1 and 2 first. Unsupervised noise labels are candidates for review, not confirmed faults.

This entry point runs the implementation files in this folder in order and stops on an error. Its authoritative results, plots and intermediate files are written directly to this folder’s `outputs/`. Some large preprocessing intermediates are kept locally and excluded from Git.

## Implementation

- [07_detect_battery_anomalies.py](07_detect_battery_anomalies.py)

## Results and plots

- [outputs/07_anomaly_detection/](outputs/07_anomaly_detection/)

Additional investigation utility: `investigate_battery_anomalies.py`.
