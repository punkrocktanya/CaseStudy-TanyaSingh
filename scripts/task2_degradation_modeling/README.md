# Task 2: Advanced degradation modeling

Analyze capacity fade, fit empirical and square-root-time models, compare statistical, physics-inspired and ML methods, and explore dV/dQ signatures with sensitivity checks.

## Run

From the project root:

```bash
python scripts/task2_degradation_modeling/task2_degradation_modeling.py
```

Run Task 1 first. The analysis is in outputs/06_differential_voltage/task2_analysis.md; feature positions do not identify LLI/LAM on their own.

This entry point runs the validated pipeline stages below in order and then copies their reviewable results into this folder. It stops on an error. The authoritative working outputs remain in `scripts/outputs/`; copies are refreshed only when this task runs. Intermediate Excel workbooks, cleaned Parquet files and per-row interval diagnostics are omitted from the copies to avoid duplicating large files.

## Implementation

- [stage_04_fit_capacity_fade.py](../stage_04_fit_capacity_fade.py)
- [05_compare_capacity_models.py](../05_compare_capacity_models.py)
- [06_differential_voltage.py](../06_differential_voltage.py)
- [task2_analysis_summary.py](../task2_analysis_summary.py)

## Results and plots

- [outputs/04_capacity_fade/](outputs/04_capacity_fade/)
- [outputs/05_capacity_model_comparison/](outputs/05_capacity_model_comparison/)
- [outputs/06_differential_voltage/](outputs/06_differential_voltage/)
