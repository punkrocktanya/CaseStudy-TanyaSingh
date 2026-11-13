# Task 1: Data engineering and preprocessing

Read both source Excel workbooks, normalize and validate measurements, classify charge/discharge/rest, and calculate cycle-level C-rate, coulombic efficiency, duration and energy throughput. Missing temperature and quality issues are recorded.

## Run

From the project root:

```bash
python scripts/task1_data_engineering/task1_preprocess.py
```

The two LR1865SZ Excel files must be in the project root. This task generates the intermediate data required by later tasks.

This entry point runs the implementation files in this folder in order and stops on an error. Its authoritative results, plots and intermediate files are written directly to this folder’s `outputs/`. Some large preprocessing intermediates are kept locally and excluded from Git.

## Implementation

- [run_cleaning_pipeline.py](run_cleaning_pipeline.py)

## Results and plots

- [outputs/01_data_cleaning/](outputs/01_data_cleaning/)
- [outputs/02_silver_phase_data/](outputs/02_silver_phase_data/)
- [outputs/03_gold_cycle_features/](outputs/03_gold_cycle_features/)

Supporting files include `battery_config.py`, `battery_validated_pipeline.py`, `battery_data_audit_parquet.py` and `test_battery_validated_pipeline.py`.
