# Task 2: Advanced degradation modeling

Analyze capacity fade, fit empirical and square-root-time models, compare statistical, physics-inspired and ML methods, and explore dV/dQ signatures with sensitivity checks.

## Run

From the project root:

```bash
python scripts/task2_degradation_modeling/task2_degradation_modeling.py
```

Run Task 1 first. The analysis is in outputs/06_differential_voltage/task2_analysis.md; feature positions do not identify LLI/LAM on their own.

This entry point runs the implementation files in this folder in order and stops on an error. Its authoritative results, plots and intermediate files are written directly to this folder’s `outputs/`. Some large preprocessing intermediates are kept locally and excluded from Git.

## Implementation

- [stage_04_fit_capacity_fade.py](stage_04_fit_capacity_fade.py)
- [05_compare_capacity_models.py](05_compare_capacity_models.py)
- [06_differential_voltage.py](06_differential_voltage.py)
- [task2_analysis_summary.py](task2_analysis_summary.py)

## Results and plots

- [outputs/04_capacity_fade/](outputs/04_capacity_fade/)
- [outputs/05_capacity_model_comparison/](outputs/05_capacity_model_comparison/)
- [outputs/06_differential_voltage/](outputs/06_differential_voltage/)

Additional review and test files: `stage_04_review_capacity_models.py` and `test_task2_summary.py`.
