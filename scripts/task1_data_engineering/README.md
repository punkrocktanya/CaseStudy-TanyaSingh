# Task 1: Data engineering and preprocessing

Read both source Excel workbooks, normalize and validate measurements, classify charge/discharge/rest, and calculate cycle-level C-rate, coulombic efficiency, duration and energy throughput. Missing temperature and quality issues are recorded.

## Run

From the project root:

```bash
python scripts/task1_data_engineering/task1_preprocess.py
```

The two LR1865SZ Excel files must be in the project root. This task generates the intermediate data required by later tasks.

This entry point runs the validated pipeline stages below in order and then copies their reviewable results into this folder. It stops on an error. The authoritative working outputs remain in `scripts/outputs/`; copies are refreshed only when this task runs. Intermediate Excel workbooks, cleaned Parquet files and per-row interval diagnostics are omitted from the copies to avoid duplicating large files.

## Implementation

- [run_cleaning_pipeline.py](../run_cleaning_pipeline.py)

## Results and plots

- [outputs/01_data_cleaning/](outputs/01_data_cleaning/)
- [outputs/02_silver_phase_data/](outputs/02_silver_phase_data/)
- [outputs/03_gold_cycle_features/](outputs/03_gold_cycle_features/)
